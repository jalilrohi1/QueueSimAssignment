
from __future__ import annotations
from random import expovariate  # For forward references
from ..core.backup import Backup  # Import Backup if needed
from dataclasses import dataclass
from typing import Optional, List
from ..core.node import Node

def exp_rv(mean):
    """Return an exponential random variable with the given mean."""
    return expovariate(1 / mean)


class DataLost(Exception):
    """Not enough redundancy in the system, data is lost. We raise this exception to stop the simulation."""
    pass

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


