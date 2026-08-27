# MeshWeaver

import asyncio
import time

from dht import Peer

class HeartbeatMonitor:
    """
    Monitors MeshWeaver peers using periodic PING messages.
    """

    def __init__(
        self,
        node,
        interval=5,
        timeout=15
    ):
        self.node = node
        self.interval = interval
        self.timeout = timeout

        self.last_seen = {}
        self.running = False

    def mark_alive(self, node_id):
        """
        Record the latest time a peer was seen.
        """

        self.last_seen[node_id] = time.time()

    def is_alive(self, node_id):
        """
        Check whether a peer is considered alive.
        """

        last_seen = self.last_seen.get(node_id)

        if last_seen is None:
            return False

        return (
            time.time() - last_seen
        ) < self.timeout

    def get_status(self, node_id):
        """
        Return the current status of a peer.
        """

        if self.is_alive(node_id):
            return "ONLINE"

        return "OFFLINE"

    async def ping_peer(self, peer):
        """
        Send a PING message to one peer.
        """

        message = {
            "type": "PING",
            "node_id": self.node.node_id
        }

        try:
            await self.node.send_message(
                peer["host"],
                peer["port"],
                message
            )

            print(
                f"Heartbeat sent to" 
                f"{peer.node_id[:8]} "
            )

        except Exception as exc:
            print(
                f"Heartbeat failed for "
                f"{peer.node_id[:8]}: {exc}"
            )

    async def check_peers(self):
        """
        send Heartbeat message to all known peers.
        """ 

        if not hasattr(self.node, "dht"):
            return

        peers = self.node.dht.get_peers()

        for peers in peers:

            await self.ping_peer(Peer)

        self.remove_dead_peers() 

    def remove_dead_peers(self):
        """
        Remove peers that have not responded
        within the timeout period.
        """
        if not hasattr(self.node, "dht"):
            return

        dead_nodes = []

        for peer in self.node.dht.get_peers():

            if not self.is_alive(peer.node_id):

                dead_nodes.append(
                    peer.node_id
                )

        for node_id in dead_nodes:

            print(
                f"peer{node_id[:8]} "
                f"is OFFLINE"
            )

            self.node.dht.remove_peer(
                node_id
            )
              
    async def run(self):
        """
        Continuously monitor peers.
        """
            
        self.running = True
            
        print(
            f"Heartbeat monitor started "
            f"(interval={self.interval}s, "
            f"timeout={self.timeout}s)"
        )

        while self.running:

            try:

                await self.check_peers()

            except Exception as exc:

                print(
                    f"Heartbeat error: {exc}"
                )

            await asyncio.sleep(
                self.interval
            )
            
    def stop(self):
        """
        Stop heartbeat monitoring.
        """

        self.running = False

        print(
            "Heartbeat monitor stopped"
        )
