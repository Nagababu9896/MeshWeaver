# MeshWeaver


import asyncio
import sys
import time

from dht import KademliaDHT
from gossip import GossipEngine
from heartbeat import HeartbeatMonitor
from registry import create_default_registry
from scheduler import TaskScheduler
from security import MessageSecurity
from transport import Transport


class MeshNode:

    def __init__(self, host="127.0.0.1", port=9000):

        self.node_id = __import__("uuid").uuid4().hex

        self.host = host
        self.port = port

        self.transport = Transport(self)

        self.registry = create_default_registry()

        self.dht = KademliaDHT(self.node_id)

        self.scheduler = TaskScheduler(self)

        self.gossip = GossipEngine(
            self,
            interval=5
        )

        self.heartbeat = HeartbeatMonitor(
            self,
            interval=5,
            timeout=15
        )

        self.security = MessageSecurity(
            "meshweaver-secret"
        )

        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.running = False

    async def start(self):

        print("=" * 50)
        print("MeshWeaver Node")
        print("=" * 50)

        print(f"Node ID : {self.node_id}")
        print(f"Address : {self.host}:{self.port}")

        await self.transport.start()

        self.running = True

        asyncio.create_task(
            self.gossip.start()
        )

        asyncio.create_task(
            self.heartbeat.run()
        )

        print("Node started successfully")

    async def send_message(
        self,
        host,
        port,
        message
    ):

        secured = self.security.secure_message(
            message
        )

        await self.transport.send(
            host,
            port,
            secured
        )

    async def handle_message(
        self,
        message,
        address
    ):

        if not self.security.verify_message(message):

            print(
                f"Rejected message from {address}"
            )

            return

        message_type = message.get("type")

        node_id = message.get(
            "node_id"
        )

        if message_type == "PING":

            self.dht.add_peer(
                node_id,
                address[0],
                address[1]
            )

            response = {
                "version": "1.0",
                "message_id": __import__("uuid").uuid4().hex,
                "type": "PONG",
                "node_id": self.node_id
            }

            await self.send_message(
                address[0],
                address[1],
                response
            )

            print(
                f"PING received from "
                f"{node_id[:8]}"
            )

        elif message_type == "PONG":

            self.heartbeat.mark_alive(
                node_id
            )

            print(
                f"PONG received from "
                f"{node_id[:8]}"
            )

        elif message_type == "GOSSIP":

            load = message.get(
                "load",
                {}
            )

            cpu = load.get(
                "cpu",
                0
            )

            memory = load.get(
                "memory",
                0
            )

            if self.dht.get_peer(node_id):

                self.dht.update_load(
                    node_id,
                    cpu,
                    memory
                )

            print(
                f"GOSSIP from "
                f"{node_id[:8]} "
                f"CPU={cpu}%"
            )

        elif message_type == "TASK":

            await self.handle_task(
                message,
                address
            )

        elif message_type == "TASK_RESULT":

            print(
                "Task result:",
                message
            )

    async def handle_task(
        self,
        message,
        address
    ):

        task_name = message.get(
            "task"
        )

        arguments = message.get(
            "arguments",
            []
        )

        keyword_arguments = message.get(
            "keyword_arguments",
            {}
        )

        try:

            result = self.registry.execute(
                task_name,
                arguments,
                keyword_arguments
            )

            response = {
                "version": "1.0",
                "message_id": __import__("uuid").uuid4().hex,
                "type": "TASK_RESULT",
                "node_id": self.node_id,
                "task": task_name,
                "success": True,
                "result": result
            }

        except Exception as exc:

            response = {
                "version": "1.0",
                "message_id": __import__("uuid").uuid4().hex,
                "type": "TASK_RESULT",
                "node_id": self.node_id,
                "task": task_name,
                "success": False,
                "error": str(exc)
            }

        await self.send_message(
            address[0],
            address[1],
            response
        )

    async def send_ping(
        self,
        host,
        port
    ):

        message = {
            "version": "1.0",
            "message_id": __import__("uuid").uuid4().hex,
            "type": "PING",
            "node_id": self.node_id
        }

        await self.send_message(
            host,
            port,
            message
        )

    async def stop(self):

        self.running = False

        self.gossip.stop()
        self.heartbeat.stop()

        self.transport.close()

        print("Node stopped")


async def main():

    port = 9000

    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    node = MeshNode(
        host="127.0.0.1",
        port=port
    )

    await node.start()

    print(
        f"\nNode running on port {port}"
    )

    try:

        while node.running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:

        await node.stop()


if __name__ == "__main__":
    asyncio.run(main())