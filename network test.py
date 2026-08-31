# MeshWeaver

# network_test.py

import asyncio
import uuid

from dht import KademliaDHT
from security import MessageSecurity

 
class TestNode:

    def __init__(self, port):
        self.node_id = uuid.uuid4().hex
        self.host = "127.0.0.1"
        self.port = port

        self.dht = KademliaDHT(
            self.node_id,
            k=20
        )

        self.security = MessageSecurity(
            "meshweaver-secret"
        )

        self.transport = None

    async def start(self):

        loop = asyncio.get_running_loop()

        self.transport, _ = (
            await loop.create_datagram_endpoint(
                lambda: NodeProtocol(self),
                local_addr=(
                    self.host,
                    self.port
                )
            )
        )

        print(
            f"[STARTED] "
            f"{self.node_id[:8]} "
            f"127.0.0.1:{self.port}"
        )

    async def send_ping(self, peer):

        message = {
            "version": "1.0",
            "message_id": uuid.uuid4().hex,
            "type": "PING",
            "node_id": self.node_id
        }

        message = self.security.secure_message(
            message
        )

        data = str(message).encode()

        self.transport.sendto(
            data,
            (
                peer.host,
                peer.port
            )
        )

    def add_peer(self, node):

        if node.node_id == self.node_id:
            return

        self.dht.add_peer(
            node.node_id,
            node.host,
            node.port
        )

    def close(self):

        if self.transport:
            self.transport.close()


class NodeProtocol(asyncio.DatagramProtocol):

    def __init__(self, node):
        self.node = node

    def connection_made(self, transport):
        pass

    def datagram_received(self, data, address):

        print(
            f"[RECEIVED] "
            f"Node {self.node.node_id[:8]} "
            f"from {address}"
        )


async def main():

    print("=" * 60)
    print("MeshWeaver 10-Node Network Audit")
    print("=" * 60)

    nodes = []

    # Create 10 nodes
    for port in range(9000, 9010):

        node = TestNode(port)

        await node.start()

        nodes.append(node)

    print("\nAdding peers...")

    # Every node learns about all other nodes
    for node in nodes:

        for peer in nodes:

            node.add_peer(peer)

    print("\nNetwork status:")

    for node in nodes:

        print(
            f"Node {node.node_id[:8]} "
            f"→ {len(node.dht)} peers"
        )

    print("\nExpected:")
    print("Each node should know 9 other nodes.")

    print("\nRunning for 10 seconds...")

    await asyncio.sleep(10)

    print("\nStopping nodes...")

    for node in nodes:
        node.close()

    print("\nNetwork audit completed.")


if __name__ == "__main__":

    asyncio.run(main())