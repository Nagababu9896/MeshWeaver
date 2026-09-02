# MeshWeaver

"""
example.py — spins up a 3-node MeshWeaver mesh in a single process
(different localhost ports) and submits a batch of tasks, showing them
get distributed across nodes via least-in-flight routing.

Run:
    python example.py
"""

import asyncio
import logging

from main import MeshNode

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")


def add(a, b):
    return a + b


def square(n):
    return n * n


async def main():
    node_a = MeshNode(host="127.0.0.1", port=9101)
    node_b = MeshNode(host="127.0.0.1", port=9102)
    node_c = MeshNode(host="127.0.0.1", port=9103)

    for n in (node_a, node_b, node_c):
        await n.start()

    # give connections + one gossip round time to settle
    await asyncio.sleep(2.0)

    print("\n--- mesh formed ---")
    for n in (node_a, node_b, node_c):
        print(n.node_id, "-> running")

    print("\n--- submitting tasks from node_a ---")
    try:
        await node_a.send_task("127.0.0.1", 9102, "add", arguments=[5, 3])
        print("Task sent successfully")
    except Exception as exc:
        print(f"Error sending task: {exc}")

    print("\n--- nodes stopped ---")
    for n in (node_a, node_b, node_c):
        print(n.node_id, "-> stopped")

    for n in (node_a, node_b, node_c):
        await n.stop()


if __name__ == "__main__":
    asyncio.run(main())