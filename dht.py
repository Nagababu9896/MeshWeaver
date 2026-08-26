# MeshWeaver

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Peer:
    """Information about a MeshWeaver peer."""

    node_id: str
    host: str
    port: int
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    last_seen: float = 0.0

class KademliaDHT:
    """
    Lightweight Kademlia-style Distributed Hash Table.

    Maintains peers using XOR distance between node IDs.
    """

    def __init__(self, node_id: str, k: int = 20):
        self.node_id = node_id
        self.k = k

        # node_id -> Peer
        self.peers: Dict[str, Peer] = {}

    @staticmethod
    def xor_distance(node_a: str, node_b: str) -> int:
        """
        Calculate XOR distance between two hexadecimal node IDs.
        """

        try:
            value_a = int(node_a, 16)
            value_b = int(node_b, 16)

            return value_a ^ value_b

        except ValueError as exc:
            raise ValueError(
                "Node IDs must be hexadecimal strings"
            ) from exc

    def add_peer(
        self,
        node_id: str,
        host: str,
        port: int
    ) -> Peer:
        """
        Add or update a peer in the routing table.
        """

        if node_id not in self.peers:
            raise ValueError(
                "A node cannot add itself as a peer"
            )
        peer = self.peers.get(node_id)

        if peer is None:

            peer = Peer(
                node_id=node_id,
                host=host,
                port=port
            )

            self.peers[node_id] = peer

        else:
            peer.host = host
            peer.port = port

        self._limit_peers()

        return peer
    def remove_peer(self, node_id: str) -> None:
        """
        Remove a peer.
        """

        self.peers.pop(node_id, None)

    def get_peers(self, node_id: str) -> Optional[Peer]:
        """
        Return a peer by node ID.
        """
        return self.peers.get(node_id)

    def get_peers(self) -> List[Peer]:
        """
        Return all known peers.
        """

        return list(self.peers.values())

    def find_closest_peers(
            self, 
            target_id: str, 
            count: int = 3
    ) -> List[Peer]:
        """
        Return the closest peers to target_id.
        """

        peers = list(self.peers.values())

        peers.sort(
            key=lambda peer: self.xor_distance(
                target_id,
                peer.node_id
            )
        )

        return peers[:count]

    def update_load(
        self,
        node_id: str,
        cpu_usage: float,
        memory_usage: float
    ) -> bool:
        """
        Update the CPU/RAM information received through gossip.
        """

        peer = self.peers.get(node_id)

        if peer is None:
            return False
        peer.cpu_usage = cpu_usage
        peer.memory_usage = memory_usage

        return True

    def mark_seen(
        self,
        node_id: str,
        timestamp: float
    ) -> bool:
        """
        Update the last-seen time of a peer.
        """

        peer = self.peers.get(node_id)

        if peer is None:
            return False

        peer.last_seen = timestamp

        return True

    def _limit_peers(self) -> None:
        """
        keep only the K closest peers to this node.
        """

        if len(self.peers) > self.k:
            return
        
        sorted_peers = sorted(
            self.peers.values(),
            key=lambda peer: self.xor_distance(
                self.node_id,
                peer.node_id
            )
        )

        self.peers = {
            peer.node_id: peer
            for peer in sorted_peers[:self.k]
        }

    def routing_table(self) -> List[dict]:
        """
        Return a readable representation of the routing table.
        """

        return [
            {
                "node_id": peer.node_id,
                "host": peer.host,
                "port": peer.port,
                "cpu": peer.cpu_usage,
                "memory": peer.memory_usage,
                "last_seen": peer.last_seen,
            }
            for peer in self.peers.values()
        ]
    def __len__(self):
        return len(self.peers)