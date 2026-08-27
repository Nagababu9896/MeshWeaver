# MeshWeaver


from dataclasses import dataclass
from typing import Dict, List, Optional, Union


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
    """Lightweight Kademlia-style Distributed Hash Table."""

    def __init__(self, node_id: str, k: int = 20):
        if k <= 0:
            raise ValueError("k must be greater than zero")

        self.node_id = node_id
        self.k = k
        self.peers: Dict[str, Peer] = {}

    @staticmethod
    def xor_distance(node_a: str, node_b: str) -> int:
        """Calculate XOR distance between hexadecimal node IDs."""
        try:
            return int(node_a, 16) ^ int(node_b, 16)
        except ValueError as exc:
            raise ValueError(
                "Node IDs must be hexadecimal strings"
            ) from exc

    def add_peer(self, node_id: str, host: str, port: int) -> Peer:
        """Add or update a peer in the routing table."""
        if node_id == self.node_id:
            raise ValueError("A node cannot add itself as a peer")

        peer = self.peers.get(node_id)

        if peer is None:
            peer = Peer(node_id=node_id, host=host, port=port)
            self.peers[node_id] = peer
        else:
            peer.host = host
            peer.port = port

        self._limit_peers()
        return peer

    def remove_peer(self, node_id: str) -> None:
        """Remove a peer."""
        self.peers.pop(node_id, None)

    def get_peer(self, node_id: str) -> Optional[Peer]:
        """Return a peer by node ID."""
        return self.peers.get(node_id)

    def get_peers(self, node_id: Optional[str] = None) -> Union[Peer, List[Peer], None]:
        """Return one peer by ID, or all known peers."""
        if node_id is not None:
            return self.peers.get(node_id)

        return list(self.peers.values())

    def find_closest_peers(self, target_id: str, count: int = 3) -> List[Peer]:
        """Return the closest peers to target_id."""
        return sorted(
            self.peers.values(),
            key=lambda peer: self.xor_distance(target_id, peer.node_id),
        )[:count]

    def update_load(
        self,
        node_id: str,
        cpu_usage: float,
        memory_usage: float,
    ) -> bool:
        """Update CPU and memory information."""
        peer = self.peers.get(node_id)

        if peer is None:
            return False

        peer.cpu_usage = cpu_usage
        peer.memory_usage = memory_usage
        return True

    def mark_seen(self, node_id: str, timestamp: float) -> bool:
        """Update the last-seen time of a peer."""
        peer = self.peers.get(node_id)

        if peer is None:
            return False

        peer.last_seen = timestamp
        return True

    def _limit_peers(self) -> None:
        """Keep only the K closest peers to this node."""
        if len(self.peers) <= self.k:
            return

        sorted_peers = sorted(
            self.peers.values(),
            key=lambda peer: self.xor_distance(self.node_id, peer.node_id),
        )

        self.peers = {
            peer.node_id: peer
            for peer in sorted_peers[:self.k]
        }

    def routing_table(self) -> List[dict]:
        """Return a readable representation of the routing table."""
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

    def __len__(self) -> int:
        return len(self.peers)