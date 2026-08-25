# MeshWeaver

import asyncio
import json

class UDPTransport(asyncio.DatagramProtocol):

    def __init__(self, node):
        self.node = node
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print(f"UDP server started on {self.node.host}:{self.node.port}")

    def datagram_received(self, data, addr):
        try:
            message = json.loads(data.decode())

            print(f"Received from {addr}: {message}")

            asyncio.create_task(
                self.node.handle_message(message, addr)
            )

        except Exception as exc:
            print(f"Invalid message from {addr}: {exc}")

    def error_received(self, exc):
        print(f"UDP error: {exc}")

    def connection_lost(self, exc):
        print("UDP connection closed")

class Transport:

    def __init__(self, node):
        self.node = node
        self.transport = None

    async def start(self):
        loop = asyncio.get_running_loop()

        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: UDPTransport(self.node),
            local_addr=(self.node.host, self.node.port)
        )

    async def send(self, host, port, message):
        if self.transport is None:
            raise RuntimeError("Transport is not started")

        data = json.dumps(message).encode("utf-8")

        self.transport.sendto(
            data,
            (host, port)
        )

    def close(self):
        if self.transport:
            self.transport.close()
