# MeshWeaver


from dataclasses import dataclass
from typing import Optional


@dataclass
class NodeLoad:
    """Resource information for a node."""

    node_id: str
    cpu: float = 100.0
    memory: float = 100.0


class TaskScheduler:
    """
    Selects the best node for executing a task.

    The default strategy is to select the node
    with the lowest CPU usage.
    """

    def __init__(self, local_node):
        self.local_node = local_node

    def get_local_load(self) -> NodeLoad:
        """Get the local node's current load."""

        cpu = getattr(
            self.local_node,
            "cpu_usage",
            0.0
        )

        memory = getattr(
            self.local_node,
            "memory_usage",
            0.0
        )

        return NodeLoad(
            node_id=self.local_node.node_id,
            cpu=cpu,
            memory=memory
        )

    def get_peer_loads(self):
        """Get load information for known peers."""

        loads = []

        if not hasattr(self.local_node, "dht"):
            return loads

        for peer in self.local_node.dht.get_peers():

            loads.append(
                NodeLoad(
                    node_id=peer.node_id,
                    cpu=peer.cpu_usage,
                    memory=peer.memory_usage
                )
            )

        return loads

    def get_candidates(self):
        """Return local node and all known peers."""

        candidates = [
            self.get_local_load()
        ]

        candidates.extend(
            self.get_peer_loads()
        )

        return candidates

    def select_node(self) -> Optional[NodeLoad]:
        """
        Select the node with the lowest CPU usage.
        """

        candidates = self.get_candidates()

        if not candidates:
            return None

        selected = min(
            candidates,
            key=lambda node: node.cpu
        )

        return selected

    def select_node_balanced(self) -> Optional[NodeLoad]:
        """
        Select a node using both CPU and memory.

        Lower score means a better candidate.
        """

        candidates = self.get_candidates()

        if not candidates:
            return None

        selected = min(
            candidates,
            key=lambda node: (
                node.cpu * 0.7 +
                node.memory * 0.3
            )
        )

        return selected

    def print_status(self):
        """Display the current node loads."""

        print("\n--- MeshWeaver Node Loads ---")

        for node in self.get_candidates():

            print(
                f"Node: {node.node_id[:8]} | "
                f"CPU: {node.cpu:.2f}% | "
                f"Memory: {node.memory:.2f}%"
            )

        print("-----------------------------")

    def route_task(self, task_name):
        """
        Select the best node for a task.
        """

        selected = self.select_node()

        if selected is None:
            raise RuntimeError(
                "No available nodes"
            )

        print(
            f"Task '{task_name}' "
            f"routed to {selected.node_id[:8]} "
            f"(CPU={selected.cpu:.2f}%)"
        )

        return selected