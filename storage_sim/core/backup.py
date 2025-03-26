import logging
from random import expovariate
from typing import List

from humanfriendly import format_timespan
from .discrete_event_sim import Simulation
from .events import LogBandwidthWaste, Online, Fail, BlockBackupComplete, BlockRestoreComplete, DataLost
#from .node import exp_rv

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
            #logging.info("No Available Bandwidth for transfer")
            return
        
        uploader.available_bw_upload -= speed
        downloader.available_bw_download -= speed
        #speed = min(effective_upload_speed, effective_download_speed)
        delay = block_size / speed

        # NEW CODE: Decrement the node's available bandwidth
        #uploader.available_bw_upload = max(0, uploader.available_bw_upload - speed)
        #downloader.available_bw_download = max(0, downloader.available_bw_download - speed)

        # Create transfer event (either backup or restore)
        if restore:
            event = BlockRestoreComplete(uploader, downloader, block_id,speed)
        else:
            event = BlockBackupComplete(uploader, downloader, block_id,speed)

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
