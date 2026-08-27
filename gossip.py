# MeshWeaver

import asyncio
import os
import time

from protocol import create_gossip_message

class GossipEngine:
    """
    Periodically shares CPU and memory information
    with other MeshWeaver nodes.
    """

    def __init__(self, node, interval=5):
        self.node = node
        self.interval = interval
        self.running = False

    def get_cpu_usage(self):
        """
        Get a simple CPU load percentage.

        Uses the system load average when available.
        """
        try:
            load = os.getloadavg()[0]
            cpu_count = os.cpu_count() or 1

            usage = (load / cpu_count) * 100

            return round(
                min(max(usage, 0), 100),
                2
            )

        except (AttributeError, OSError):
            return 0.0

    def get_memory_usage(self):
        """
        Return memory usage.

        This implementation intentionally avoids
        external dependencies.
        """

        return 0.0

    def get_system_load(self):
        """
        Return the node's current resource information.
        """

        return {
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "timestamp": time.time()
        }
    async def send_gossip(self):
        """
        Send the current resource information 
        to all known peers.
        """
        load = self.get_system_load()

        message = create_gossip_message(
            self.node.node_id,
            load
        )

        peers = self.node.dht.get_peers()

        for peer in peers:
            try:
                await self.node.send_message(
                    peer.host,
                    peer.port,
                    message
                )

                print(
                    f"Gossip sent to"
                    f"{peer.node_id[:8]} "
                    f"CPU={load['cpu']}% "
                )

            except Exception as exc:

                print(
                    f"Gossip failed for"
                    f"{peer.node_id[:8]}: {exc}"
                )

    async def start(self):
        """
        RUN gossip continuously.
        """           
        self.running = True

        print(
            f"Gossip engine started "
            f"(interval={self.interval}s)"
        )   

        while self.running:

            try:

                await self.send_gossip()

            except Exception as exc:

                print(
                    f"Gossip error: {exc}"
                )

            await asyncio.sleep(
                self.interval
            )

    def stop(self):
        """
        Stop the gossip engine.
        """

        self.running = False

        print(
            "Gossip engine stopped"
        )