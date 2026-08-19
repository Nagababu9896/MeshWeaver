# MeshWeaver
import hashlib
import logging
import uuid

def generate_node_id(host: str, port: int) -> str:
    """
    Generate a deterministic node ID from host and port.
    """

    value = f"{host}:{port}"

    return hashlib.sha1(
        value.encode("utf-8")
    ).hexdigest()

def generate_task_id() -> str:
    return str(uuid.uuid4())

def setup_logging(node_id: str):
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            f"NODE={node_id[:8]} | "
            "%(levelname)s | "
            "%(message)s"
        ),
    )

def xor_distance(node_a: str, node_b: str) -> int:
    return int(node_a, 16) ^ int(node_b, 16)
