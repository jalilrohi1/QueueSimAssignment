
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

#if TYPE_CHECKING:
#    from .backup import Backup  # only used for type checking

from ..utils.events import TransferComplete


@dataclass(eq=False)  # auto initialization from parameters below (won't consider two nodes with same state as equal)
class Node:
    """Class representing the configuration of a given node."""

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
        if not sim.parallel_up_down and self.current_uploads:
            return False

        # First, attempt to restore a missing block from a peer.
        for peer in self.rank_peers():
            block_id = self.remote_blocks_held.get(peer)
            # Ensure block_id is valid and the block is missing locally.
            if block_id is None or block_id >= len(self.local_blocks):
                continue
            if not self.local_blocks[block_id] and peer.online and not peer.current_downloads:
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

