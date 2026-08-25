# MeshWeaver

import asyncio
import uuid

from transport import Transport
from registry import create_default_registry


class MeshNode:

    def __init__(self, host="127.0.0.1", port=9000):

        self.node_id = uuid.uuid4().hex
        self.host = host
        self.port = port

        self.transport = Transport(self)
        self.registry = create_default_registry()

        self.running = False

    async def start(self):

        print("=" * 50)
        print("MeshWeaver Node")
        print("=" * 50)

        print(f"Node ID : {self.node_id}")
        print(f"Address : {self.host}:{self.port}")

        await self.transport.start()

        self.running = True

        print("Node started successfully")
        print("Available tasks:")
        print(self.registry.list_tasks())

    async def send_message(self, host, port, message):

        await self.transport.send(
            host,
            port,
            message
        )

    async def handle_message(self, message, address):

        message_type = message.get("type")

        if message_type == "PING":

            response = {
                "type": "PONG",
                "node_id": self.node_id
            }

            await self.send_message(
                address[0],
                address[1],
                response
            )

            print(f"PONG sent to {address}")

        elif message_type == "PONG":

            print(
                f"PONG received from {address}"
            )

        elif message_type == "TASK":

            await self.handle_task(
                message,
                address
            )

        else:

            print(
                f"Unknown message type: {message_type}"
            )

    async def handle_task(self, message, address):

        task_name = message.get("task")

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
                "type": "TASK_RESULT",
                "success": True,
                "task": task_name,
                "result": result
            }

        except Exception as exc:

            response = {
                "type": "TASK_RESULT",
                "success": False,
                "task": task_name,
                "error": str(exc)
            }

        await self.send_message(
            address[0],
            address[1],
            response
        )

    async def send_ping(self, host, port):

        message = {
            "type": "PING",
            "node_id": self.node_id
        }

        await self.send_message(
            host,
            port,
            message
        )

    async def send_task(
        self,
        host,
        port,
        task_name,
        arguments=None,
        keyword_arguments=None
    ):

        message = {
            "type": "TASK",
            "node_id": self.node_id,
            "task": task_name,
            "arguments": arguments or [],
            "keyword_arguments": keyword_arguments or {}
        }

        await self.send_message(
            host,
            port,
            message
        )

    async def stop(self):

        self.running = False

        self.transport.close()

        print("Node stopped")


async def main():

    node = MeshNode(
        host="127.0.0.1",
        port=9000
    )

    await node.start()

    print("\nMeshWeaver is running...")
    print("Press CTRL+C to stop.")

    try:

        while node.running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:

        await node.stop()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        pass
    