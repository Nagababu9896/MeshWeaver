# MeshWeaver
import hashlib
import logging
import socket
import time
import uuid

from config import Config


def generate_node_id():
    """
    Generate a unique node ID.
    """
    unique_value = (
        f"{socket.gethostname()}-"
        f"{uuid.uuid4()}-"
        f"{time.time()}"
    )
    return hashlib.sha256(
        unique_value.encode("utf-8")
    ).hexdigest()

def generate_message_id():
    """
    Generate a unique message ID.
    """
    return uuid.uuid4().hex

def get_timestamp():
    """
    Return the current Unix timestamp.
    """
    return time.time()

def get_local_ip():
    """
    Try to determine the local machine IP address.
    """
    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )
        sock.connect(("8.8.8.8", 80))

        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except OSError:
        return "127.0.0.1"

def setup_logging():
    """
    Configure application logging.
    """
    logging.basicConfig(
        level=getattr(
            logging,
            Config.LOG_LEVEL.upper(), 
            logging.INFO
        ),
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )

    return logging.getLogger("MeshWeaver")


def get_logger(name):
    """
    Return a Logger instance with the specified name.
    """
    return logging.getLogger(name)

def validate_node_id(node_id):
    """
    Validate a node ID.
    """
    if not isinstance(node_id, str):
        return False

    if not node_id:
        return False

    return True

def safe_int(value, default=0):
    """
    Safely convert a value to integer.
    """

    try:
        return int(value)

    except (TypeError, ValueError):
        return default

def safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    """

    try:
        return float(value)

    except (TypeError, ValueError):
        return default

def format_address(host, port):
    """
    Format a network address.
    """

    return f"{host}:{port}"


def calculate_xor_distance(node_a, node_b):
    """
    Calculate XOR distance between two hexadecimal node IDs.

    Used by the Kademlia DHT.
    """

    try:
        value_a = int(node_a, 16)
        value_b = int(node_b, 16)

        return value_a ^ value_b

    except ValueError as exc:
        raise ValueError(
            "Node IDs must behexadecimal strings"
        ) from exc

def is_port_available(host, port):
    """
    Check whether a TCP/UDP port is available.
    """

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:
        sock.bind((host, port))
        return True

    except OSError:
        return False

    finally:
        sock.close()
    