#!/usr/bin/env python

import argparse
import configparser
import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)  # suppress matplotlib logging
import random
from dataclasses import dataclass
from random import expovariate
from typing import Optional, List

import matplotlib.pyplot as plt
import numpy as np

# the humanfriendly library (https://humanfriendly.readthedocs.io/en/latest/) lets us pass parameters in human-readable
# format (e.g., "500 KiB" or "5 days"). You can safely remove this if you don't want to install it on your system, but
# then you'll need to handle sizes in bytes and time spans in seconds--or write your own alternative.
# It should be trivial to install (e.g., apt install python3-humanfriendly or conda/pip install humanfriendly).
from humanfriendly import format_timespan, parse_size, parse_timespan

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from libs.discrete_event_sim import Simulation, Event


def exp_rv(mean):
    """Return an exponential random variable with the given mean."""
    return expovariate(1 / mean)


class DataLost(Exception):
    """Not enough redundancy in the system, data is lost. We raise this exception to stop the simulation."""
    pass
class Backup(Simulation):
    """Backup simulation.
    """

    # type annotations for `Node` are strings here to allow a forward declaration:
    # https://stackoverflow.com/questions/36193540/self-reference-or-forward-reference-of-type-annotations-in-python
    def __init__(self, nodes: List['Node'],parallel_up_down: bool = False):
        super().__init__()  # call the __init__ method of parent class
        self.nodes = nodes
        self.online_nodes = {}  # Track the number of online nodes over time
        self.parallel_up_down = parallel_up_down  # Allow parallel uploads and downloads
        self.transfer_counts = {}  # dictionary to track number of transfers per time step
        self.schedule(0, LogBandwidthWaste())  # Start periodic bandwidth logging
        self.dw_bw_wasted = {}  # Track download bandwidth wasted
        self.up_bw_wasted = {}  # Track upload bandwidth wasted
        self.failure_events = {}  # Track node failure events
        # we add to the event queue the first event of each node going online and of failing
        for node in nodes:
            self.schedule(node.arrival_time, Online(node))
            self.schedule(node.arrival_time + exp_rv(node.average_lifetime), Fail(node))


    def register_bw_waste(self, time):
        """Tracks bandwidth waste at each time step."""
        up_waste = [node.upload_speed - node.available_bw_upload for node in self.nodes if node.online]
        dw_waste = [node.download_speed - node.available_bw_download for node in self.nodes if node.online]

        self.up_bw_wasted[time] = sum(up_waste) / len(up_waste) if up_waste else 0
        self.dw_bw_wasted[time] = sum(dw_waste) / len(dw_waste) if dw_waste else 0

        # Debugging Output
        print(f"Time {time}: Upload Waste: {self.up_bw_wasted[time]}, Download Waste: {self.dw_bw_wasted[time]}")

    
    def schedule_transfer(self, uploader: 'Node', downloader: 'Node', block_id: int, restore: bool):
        block_size = downloader.block_size if restore else uploader.block_size

        # Calculate effective bandwidth considering current active transfers
        uploader_active = len(uploader.current_uploads) + 1
        downloader_active = len(downloader.current_downloads) + 1

        effective_upload_speed = uploader.upload_speed / uploader_active
        effective_download_speed = downloader.download_speed / downloader_active

        speed = min(uploader.available_bw_upload, downloader.available_bw_download)
        if speed <= 0:
            #assert speed > 0, "No available bandwidth for transfer"
            logging.info("No Available Bandwidth for transfer")
            return
        
        uploader.available_bw_upload -= speed
        downloader.available_bw_download -= speed
        # speed = min(effective_upload_speed, effective_download_speed)
        delay = block_size / speed

        # NEW CODE: Decrement the node's available bandwidth
        # uploader.available_bw_upload = max(0, uploader.available_bw_upload - speed)
        # downloader.available_bw_download = max(0, downloader.available_bw_download - speed)

        # Create transfer event (either backup or restore)
        if restore:
            event = BlockRestoreComplete(uploader, downloader, block_id)
        else:
            event = BlockBackupComplete(uploader, downloader, block_id)

        self.schedule(delay, event)

        # Track the transfer in parallel lists
        uploader.current_uploads.append(event)
        downloader.current_downloads.append(event)


        
        #self.register_bw_waste(self.t) ###########llllllllllll

        # self.log_info(f"scheduled {event.__class__.__name__} from {uploader} to {downloader}"
        #               f" in {format_timespan(delay)}")

    def log_info(self, msg):
        """Override method to get human-friendly logging for time."""

        logging.info(f'{format_timespan(self.t)}: {msg}')

class LogBandwidthWaste:
    """A periodic event that logs bandwidth waste at fixed intervals."""
    
    def __init__(self):
        pass  # No initialization needed

    def process(self, sim: Backup):
        """Logs bandwidth waste and re-schedules itself for the next interval."""
        #print(f"Logging bandwidth waste at time {sim.t}")
        sim.register_bw_waste(sim.t)  # Log bandwidth waste
        interval = 3600 * 24  # Log every simulated day (adjustable)
        sim.schedule(sim.t + interval, LogBandwidthWaste())  # Schedule next log
    
    def __lt__(self, other):
        """Defines event priority for heap queue."""
        return isinstance(other, Online)  # Ensure LogBandwidthWaste runs after Online events

@dataclass(eq=False)  # auto initialization from parameters below (won't consider two nodes with same state as equal)
class Node:
    """Class representing the configuration of a given node."""

    # using dataclass is (for our purposes) equivalent to having something like
    # def __init__(self, description, n, k, ...):
    #     self.n = n
    #     self.k = k
    #     ...
    #     self.__post_init__()  # if the method exists

    name: str  # the node's name

    n: int  # number of blocks in which the data is encoded
    k: int  # number of blocks sufficient to recover the whole node's data

    data_size: int  # amount of data to back up (in bytes)
    storage_size: int  # storage space devoted to storing remote data (in bytes)

    upload_speed: float  # node's upload speed, in bytes per second
    download_speed: float  # download speed

    average_uptime: float  # average time spent online
    average_downtime: float  # average time spent offline

    average_lifetime: float  # average time before a crash and data loss
    average_recover_time: float  # average time after a data loss

    arrival_time: float  # time at which the node will come online

    def __post_init__(self):
        """Compute other data dependent on config values and set up initial state."""

        # whether this node is online. All nodes start offline.
        self.online: bool = False

        # whether this node is currently under repairs. All nodes are ok at start.
        self.failed: bool = False

        # size of each block
        self.block_size: int = self.data_size // self.k if self.k > 0 else 0

        # amount of free space for others' data -- note we always leave enough space for our n blocks
        self.free_space: int = self.storage_size - self.block_size * self.n

        assert self.free_space >= 0, "Node without enough space to hold its own data"

        # local_blocks[block_id] is true if we locally have the local block
        # [x] * n is a list with n references to the object x
        self.local_blocks: list[bool] = [True] * self.n

        # backed_up_blocks[block_id] is the peer we're storing that block on, or None if it's not backed up yet;
        # we start with no blocks backed up
        self.backed_up_blocks: list[Optional[Node]] = [None] * self.n

        # (owner -> block_id) mapping for remote blocks stored
        self.remote_blocks_held: dict[Node, int] = {}

        # current uploads and downloads, stored as a reference to the relative TransferComplete event
        #self.current_upload: Optional[TransferComplete] = None
        #self.current_download: Optional[TransferComplete] = None
        # Replace single transfer tracking with lists for parallel transfers
        self.current_uploads: List[TransferComplete] = []
        self.current_downloads: List[TransferComplete] = []
        
        self.available_bw_upload: float = self.upload_speed  # Set initial upload bandwidth
        self.available_bw_download: float = self.download_speed  # Set initial download bandwidth

        self.successful_transfers: int = 0  # Tracks successful transfers


    def find_block_to_back_up(self):
        """Returns the block id of a block that needs backing up, or None if there are none."""

        # find a block that we have locally but not remotely
        # check `enumerate` and `zip`at https://docs.python.org/3/library/functions.html
        for block_id, (held_locally, peer) in enumerate(zip(self.local_blocks, self.backed_up_blocks)):
            if held_locally and peer is None:
                return block_id
        return None

    def rank_peers(self):
        """Ranks peers based on past data exchanges (tit-for-tat), avoiding redundant backups."""
        #return sorted(self.remote_blocks_held.keys(), key=lambda peer: peer.successful_transfers, reverse=True)
        return sorted(
                self.remote_blocks_held.keys(),
                key=lambda peer: (peer.successful_transfers, -sum(peer.local_blocks)), 
                reverse=True
            )


    def schedule_next_upload(self, sim: Backup) -> bool:
        """Attempt to schedule the next upload. Returns True if a transfer was scheduled."""
        assert self.online

        # If parallel transfers are disabled and there’s already an active upload, do nothing.
        if sim.parallel_up_down:
            if self.available_bw_upload == 0:
                return False
        else:
            if self.current_uploads:
                return False

        # First, attempt to restore a missing block from a peer.
        for peer in self.rank_peers():
            block_id = self.remote_blocks_held.get(peer)
            # Ensure block_id is valid and the block is missing locally.
            if block_id is None or block_id >= len(self.local_blocks):
                continue
            
            if not self.local_blocks[block_id] and peer.online and peer.available_bw_download > 0:
            # if not self.local_blocks[block_id] and peer.online and not peer.current_downloads:
                sim.schedule_transfer(peer, self, block_id, restore=True)
                return True

        # Next, try to back up a block to a remote node.
        block_id = self.find_block_to_back_up()
        if block_id is None:
            return False

        # Avoid backing up to nodes that already have our blocks.
        remote_owners = {node for node in self.backed_up_blocks if node is not None}
        for peer in sim.nodes:
            if (peer is not self and peer.online and peer not in remote_owners 
                and not peer.current_downloads and peer.free_space >= self.block_size):
                sim.schedule_transfer(self, peer, block_id, restore=False)
                return True

        return False


    def schedule_next_download(self, sim: Backup) -> bool:
        """Attempt to schedule the next download. Returns True if a transfer was scheduled."""
        assert self.online

        # If parallel transfers are disabled and there’s already an active download, do nothing.
        if not sim.parallel_up_down and self.current_downloads:
            return False

        # First, look for a missing block to restore.
        for block_id, (held_locally, peer) in enumerate(zip(self.local_blocks, self.backed_up_blocks)):
            if not held_locally and peer is not None and peer.online and not peer.current_uploads:
                sim.schedule_transfer(peer, self, block_id, restore=True)
                return True

        # Next, try to assist a peer by backing up one of their blocks.
        for peer in sim.nodes:
            if (peer is not self and peer.online and not peer.current_uploads 
                and self not in peer.remote_blocks_held and self.free_space >= peer.block_size):
                block_id = peer.find_block_to_back_up()
                if block_id is not None:
                    sim.schedule_transfer(peer, self, block_id, restore=False)
                    return True

        return False


    def schedule_next_uploads(self, sim: Backup):
        """Schedule multiple uploads in parallel if allowed."""
        counter = 0
        while counter < 1 or sim.parallel_up_down:  # Allow multiple uploads
            if not self.schedule_next_upload(sim):  # Calls your existing upload function
                break
            counter += 1  # Track how many uploads we scheduled

    def schedule_next_downloads(self, sim: Backup):
        """Schedule multiple downloads in parallel if allowed."""
        counter = 0
        while counter < 1 or sim.parallel_up_down:  # Allow multiple downloads
            if not self.schedule_next_download(sim):  # Calls your existing download function
                break
            counter += 1  # Track how many downloads we scheduled


    def __hash__(self):
        """Function that allows us to have `Node`s as dictionary keys or set items.

        With this implementation, each node is only equal to itself.
        """
        return id(self)

    def __str__(self):
        """Function that will be called when converting this to a string (e.g., when logging or printing)."""

        return self.name


@dataclass
class NodeEvent(Event):
    """An event regarding a node. Carries the identifier, i.e., the node's index in `Backup.nodes_config`"""

    node: Node

    def process(self, sim: Simulation):
        """Must be implemented by subclasses."""
        raise NotImplementedError


class Online(NodeEvent):
    """A node goes online."""

    def process(self, sim: Backup):
        node = self.node
        sim.online_nodes[sim.t] = sim.online_nodes.get(sim.t, 0) + 1  # Increase count
        if node.online or node.failed:
            return
        node.online = True
        
        # Reset bandwidth when a node comes online
        node.available_bw_upload = node.upload_speed
        node.available_bw_download = node.download_speed
        
        # schedule next upload and download
        #node.schedule_next_upload(sim)
        #node.schedule_next_download(sim)
        
        #Reset bandwidth when a node comes online
        node.available_bw_upload = node.upload_speed
        node.available_bw_download = node.download_speed
        
        node.schedule_next_uploads(sim)
        node.schedule_next_downloads(sim)
        
        #Register bandwidth waste when a node connects
        sim.register_bw_waste(sim.t)
        
        # schedule the next offline event
        sim.schedule(exp_rv(node.average_uptime), Offline(node))


class Recover(Online):
    """A node goes online after recovering from a failure."""

    def process(self, sim: Backup):
        node = self.node
        sim.log_info(f"{node} recovers")
        node.failed = False
        node.online = True  # Ensure node is set online
        
        # Reset bandwidth for a recovering node
        node.available_bw_upload = node.upload_speed
        node.available_bw_download = node.download_speed
        
        node.schedule_next_uploads(sim)  # Schedule multiple uploads
        node.schedule_next_downloads(sim)  # Schedule multiple downloads
        #super().process(sim)
        sim.schedule(exp_rv(node.average_lifetime), Fail(node))


class Disconnection(NodeEvent):
    """Base class for both Offline and Fail, events that make a node disconnect."""

    def process(self, sim: Simulation):
        """Must be implemented by subclasses."""
        raise NotImplementedError
    def disconnect(self):
        node = self.node
        node.online = False

        # Cancel all active uploads
        for transfer in node.current_uploads:
            transfer.canceled = True
            # Remove the transfer from the downloader's current_downloads list if present
            if transfer in transfer.downloader.current_downloads:
                transfer.downloader.current_downloads.remove(transfer)
        node.current_uploads.clear()

        # Cancel all active downloads
        for transfer in node.current_downloads:
            transfer.canceled = True
            # Remove the transfer from the uploader's current_uploads list if present
            if transfer in transfer.uploader.current_uploads:
                transfer.uploader.current_uploads.remove(transfer)
        node.current_downloads.clear()



class Offline(Disconnection):
    """A node goes offline."""

    def process(self, sim: Backup):
        node = self.node
        sim.online_nodes[sim.t] = sim.online_nodes.get(sim.t, 0) - 1  # Decrease count
        if node.failed or not node.online:
            return
        assert node.online
        self.disconnect()
        # schedule the next online event
        sim.schedule(exp_rv(self.node.average_downtime), Online(node))


class Fail(Disconnection):
    """A node fails and loses all local data."""

    def process(self, sim: Backup):
        #sim.log_info(f"Data lost: {sum(node.failed for node in sim.nodes)}")
        lost_blocks = sum(1 for block in self.node.local_blocks if block)
        sim.log_info(f"{self.node} fails - {lost_blocks} blocks lost")

        self.disconnect()
        node = self.node
        node.failed = True
        node.local_blocks = [False] * node.n  # lose all local data
        
        #Log failure time
        if sim.t not in sim.failure_events:
            sim.failure_events[sim.t] = 0
        sim.failure_events[sim.t] += 1  # Count failures
        
        # lose all remote data
        for owner, block_id in node.remote_blocks_held.items():
            owner.backed_up_blocks[block_id] = None
            if owner.online and not owner.current_uploads:
                #owner.schedule_next_upload(sim)  # this node may want to back up the missing block
                sim.schedule(sim.t + 3600, DelayedUploadEvent(owner))  # Introduce a 1-hour delay
                sim.register_bw_waste(sim.t) #Register bandwidth waste when a node fails ########llllllll
                
        node.remote_blocks_held.clear()
        node.free_space = node.storage_size - node.block_size * node.n
        # schedule the next online and recover events
        recover_time = exp_rv(node.average_recover_time)
        sim.schedule(recover_time, Recover(node))
        

class DelayedUploadEvent:
    """Event to schedule an upload after a delay."""
    
    def __init__(self, node):
        self.node = node

    def process(self, sim: Backup):
        """Process the delayed upload event."""
        if self.node.online and not self.node.current_uploads:
            self.node.schedule_next_upload(sim)  # Now it runs at the right time
    def __lt__(self, other):
        """Defines event priority for heap queue."""
        return isinstance(other, LogBandwidthWaste)  # Ensure delayed uploads run before bandwidth logging

@dataclass
class TransferComplete(Event):
    """An upload is completed."""

    uploader: Node
    downloader: Node
    block_id: int
    canceled: bool = False

    def __post_init__(self):
        assert self.uploader is not self.downloader

    def process(self, sim: Backup):
        sim.log_info(f"Successful transfer: Block {self.block_id} from {self.uploader} to {self.downloader}")
        if self.canceled:
            return  # this transfer was canceled, so ignore this event
        uploader, downloader = self.uploader, self.downloader
        assert uploader.online and downloader.online
        self.update_block_state()
        
        self.uploader.successful_transfers += 1
        self.downloader.successful_transfers += 1
        
        #Register bandwidth waste at each transfer completion
        sim.register_bw_waste(sim.t)
        
        # Track the number of transfers at each time step
        if sim.t not in sim.transfer_counts:
            sim.transfer_counts[sim.t] = 0
        sim.transfer_counts[sim.t] += 1  # Increase count for this time step

        
        if self in uploader.current_uploads:
            uploader.current_uploads.remove(self)
        if self in downloader.current_downloads:
            downloader.current_downloads.remove(self)

        uploader.schedule_next_upload(sim)
        downloader.schedule_next_download(sim)
        

        
        for node in [uploader, downloader]:
            sim.log_info(f"{node}: {sum(node.local_blocks)} local blocks, "
                         f"{sum(peer is not None for peer in node.backed_up_blocks)} backed up blocks, "
                         f"{len(node.remote_blocks_held)} remote blocks held")

    def update_block_state(self):
        """Needs to be specified by the subclasses, `BackupComplete` and `DownloadComplete`."""
        raise NotImplementedError


class BlockBackupComplete(TransferComplete):

    def update_block_state(self):
        owner, peer = self.uploader, self.downloader
        peer.free_space -= owner.block_size
        assert peer.free_space >= 0
        owner.backed_up_blocks[self.block_id] = peer
        peer.remote_blocks_held[owner] = self.block_id


class BlockRestoreComplete(TransferComplete):
    def update_block_state(self):
        owner = self.downloader
        owner.local_blocks[self.block_id] = True
        if sum(owner.local_blocks) == owner.k:  # we have exactly k local blocks, we have all of them then
            # Optionally, log that the node's data has been fully restored.
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="configuration file")
    parser.add_argument("--max-t", default="100 years")
    parser.add_argument("--seed", help="random seed")
    parser.add_argument("--verbose", action='store_true')
    parser.add_argument("--parallel", action='store_true', help="Enable parallel uploads and downloads")

    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)  # set a seed to make experiments repeatable
    if args.verbose:
        logging.basicConfig(format='{levelname}:{message}', level=logging.INFO, style='{')  # output info on stdout

    # functions to parse every parameter of peer configuration
    parsing_functions = [
        ('n', int), ('k', int),
        ('data_size', parse_size), ('storage_size', parse_size),
        ('upload_speed', parse_size), ('download_speed', parse_size),
        ('average_uptime', parse_timespan), ('average_downtime', parse_timespan),
        ('average_lifetime', parse_timespan), ('average_recover_time', parse_timespan),
        ('arrival_time', parse_timespan)
    ]

    config = configparser.ConfigParser()
    config.read(args.config)
    nodes = []  # we build the list of nodes to pass to the Backup class
    for node_class in config.sections():
        class_config = config[node_class]
        # list comprehension: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
        cfg = [parse(class_config[name]) for name, parse in parsing_functions]
        # the `callable(p1, p2, *args)` idiom is equivalent to `callable(p1, p2, args[0], args[1], ...)
        nodes.extend(Node(f"{node_class}-{i}", *cfg) for i in range(class_config.getint('number')))
    sim = Backup(nodes,parallel_up_down=args.parallel)
    sim.run(parse_timespan(args.max_t))
    sim.log_info(f"Simulation over")

    import numpy as np
    from plot_utils import (
        plot_bandwidth_waste,
        plot_smoothed_bandwidth_waste,
        plot_data_transfers,
        plot_used_vs_wasted_bandwidth,
        plot_bandwidth_waste_distribution,
        plot_failures_vs_bandwidth_waste,
        plot_failures_vs_bandwidth_waste_with_availability,
        plot_used_vs_wasted_bandwidth_dual_axis
    )

    # Convert seconds to years
    times = np.array([t / (365 * 24 * 60 * 60) for t in sim.up_bw_wasted.keys()])
    upload_waste = np.array(list(sim.up_bw_wasted.values()))
    download_waste = np.array(list(sim.dw_bw_wasted.values()))

    transfer_times = np.array([t / (365 * 24 * 60 * 60) for t in sim.transfer_counts.keys()])
    transfer_counts = np.array(list(sim.transfer_counts.values()))

    # Compute used bandwidth
    used_bandwidth = upload_waste + download_waste
    wasted_bandwidth = upload_waste + download_waste

    # Only access `failure_events` if it exists
    if hasattr(sim, "failure_events") and sim.failure_events:
        failure_times = np.array([t / (365 * 24 * 60 * 60) for t in sim.failure_events.keys()])
        failure_counts = np.array(list(sim.failure_events.values()))

        # Generate plots including failures
        plot_failures_vs_bandwidth_waste(failure_times, failure_counts, times, upload_waste, download_waste)

    # Generate standard plots
    plot_bandwidth_waste(times, upload_waste, download_waste)
    plot_smoothed_bandwidth_waste(times, upload_waste, download_waste)
    plot_data_transfers(transfer_times, transfer_counts)
    plot_used_vs_wasted_bandwidth(times, used_bandwidth, wasted_bandwidth)
    plot_bandwidth_waste_distribution(upload_waste, download_waste)
    plot_used_vs_wasted_bandwidth_dual_axis(times, used_bandwidth, wasted_bandwidth)
    plot_failures_vs_bandwidth_waste_with_availability(failure_times, failure_counts, times, upload_waste, download_waste, sim.online_nodes)


if __name__ == '__main__':
    main()
