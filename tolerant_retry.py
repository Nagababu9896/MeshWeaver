# MeshWeaver

import asyncio
from typing import Callable, Optional


class TaskRetryManager:
    """
    Handles task retries when a remote node fails.
    """

    def __init__(
        self,
        node,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.node = node
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def get_available_nodes(self):
        """
        Return nodes that are currently available.
        """

        nodes = []

        if not hasattr(self.node, "dht"):
            return nodes

        for peer in self.node.dht.get_peers():

            nodes.append(peer)

        return nodes

    async def execute_with_retry(
        self,
        function: Callable,
        *args,
        **kwargs
    ) -> Optional[object]:
        """
        Try to execute a task remotely.
        If a node fails, retry using another node.
        """

        attempted_nodes = set()

        for attempt in range(
            self.max_retries
        ):

            candidates = [
                peer
                for peer in self.get_available_nodes()
                if peer.node_id not in attempted_nodes
            ]

            if not candidates:

                print(
                    "No unused nodes available."
                )

                break

            # Select least-loaded remaining node
            selected = min(
                candidates,
                key=lambda peer: peer.cpu_usage
            )

            attempted_nodes.add(
                selected.node_id
            )

            print(
                f"Attempt {attempt + 1}: "
                f"sending task to "
                f"{selected.node_id[:8]} "
            )

            try:

                result = await asyncio.wait_for(
                    self.node.send_serialized_task(
                        selected.host,
                        selected.port,
                        function,
                        *args,
                        **kwargs
                    ),
                    timeout=10
                )

                print(
                    f"Task executed successfully on "
                    f"{selected.node_id[:8]}"
                )

                return result

            except Exception as exc:
                
                print(
                    f"Node "
                    f"{selected.node_id[:8]}"
                    f" failed: {exc}"
                )

                # Remove failed node
                self.node.dht.remove_peer(
                    selected.node_id
                )

                if attempt < self.max_retries - 1:

                    print(
                        f"Retrying in "
                        f"in {self.retry_delay} seconds..."
                    )

                    await asyncio.sleep(
                        self.retry_delay
                    )

        raise RuntimeError(
            "Task failed after "
            f"{self.max_retries} attempts."
        )
    