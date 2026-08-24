# MeshWeaver
import os

class Config:
    """Central configuration for MeshWeaver."""

    HOST = os.getenv("MESH_HOST", "127.0.0.1")
    PORT = int(os.getenv("MESH_PORT", "9000"))

    # UDP networking
    BUFFER_SIZE = 65535
    SOCKET_TIMEOUT = 5

    # Node discovery
    DISCOVERY_INTERVAL = 5
    MAX_PEERS = 20

    # Gossip
    GOSSIP_INTERVAL = 5

    # Heartbeat
    HEARTBEAT_INTERVAL = 5
    HEARTBEAT_TIMEOUT = 15

    # Task execution
    TASK_TIMEOUT = 30

    # Logging
    LOG_LEVEL = os.getenv("MESH_LOG_LEVEL", "INFO")

    # Protocol
    PROTOCOL_VERSION = "1.0"

def get_config():
    """Return configuration as a dictionary."""

    return {
        "host": Config.HOST,
        "port": Config.PORT,
        "buffer_size": Config.BUFFER_SIZE,
        "socket_timeout": Config.SOCKET_TIMEOUT,
        "discovery_interval": Config.DISCOVERY_INTERVAL,
        "max_peers": Config.MAX_PEERS,
        "gossip_interval": Config.GOSSIP_INTERVAL,
        "heartbeat_interval": Config.HEARTBEAT_INTERVAL,
        "heartbeat_timeout": Config.HEARTBEAT_TIMEOUT,
        "task_timeout": Config.TASK_TIMEOUT,
        "log_level": Config.LOG_LEVEL,
        "protocol_version": Config.PROTOCOL_VERSION,
    }