# MeshWeaver
import json
import uuid

from config import Config


# Supported message types
PING = "PING"
PONG = "PONG"
TASK = "TASK"
TASK_RESULT = "TASK_RESULT"
GOSSIP = "GOSSIP"
HEARTBEAT = "HEARTBEAT"
PEER_REQUEST = "PEER_REQUEST"
PEER_RESPONSE = "PEER_RESPONSE"

VALID_MESSAGE_TYPES = {
    PING,
    PONG,
    TASK,
    TASK_RESULT,
    GOSSIP,
    HEARTBEAT,
    PEER_REQUEST,
    PEER_RESPONSE
}

def create_message(message_type, node_id, **data):
    """
    Create a standard MeshWeaver message.
    """

    if message_type not in VALID_MESSAGE_TYPES:
        raise ValueError(f"Unsupported message type: {message_type}")

    message = {
        "version": Config.PROTOCOL_VERSION,
        "message_id": uuid.uuid4().hex,
        "type": message_type,
        "node_id": node_id,
    }

    message.update(data)

    return message

def validate_message(message):
    """
    Validate the basic structure of a MeshWeaver message.
    """

    if not isinstance(message, dict):
        return False

    required_fields = {
        "version",
        "message_id",
        "type",
        "node_id",
    }

    if not required_fields.issubset(message.keys()):
        return False

    if message["version"] != Config.PROTOCOL_VERSION:
        return False

    if message["type"] not in VALID_MESSAGE_TYPES:
        return False 

    if not isinstance(message["node_id"], str):
        return False    

    if not isinstance(message["message_id"], str):
        return False

    return True

def encode_message(message):
    """
    
    Convert a MeshWeaver message dictionary into bytes
    for UDP transmission.
    """

    if not validate_message(message):
        raise ValueError("Invalid MeshWeaver message")

    return json.dumps(
        message,
        separators=(',', ':')
    ).encode("utf-8")

def decode_message(data):
    """
    Convert received bytes into a python dictionary.
    """

    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        message = json.loads(data)

    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"invalid message data: {exc}"
        ) from exc

    if not validate_message(message):
        raise ValueError(
            "message validation failed"
        )

    return message

def create_ping_message(node_id):
    """
    Create a PING message.
    """

    return create_message(
        PING,
        node_id,
    )    

def create_pong_message(node_id):
    """
    Create a PONG message.
    """

    return create_message(
        PONG,
        node_id,
    )

def create_task_message(
    node_id,
    task_name,
    arguments=None,
    keyword_arguments=None,
):
    """
    Create a TASK request.
    """
    return create_message(
        TASK,
        node_id,
        task=task_name,
        arguments=arguments or [],
        keyword_arguments=keyword_arguments or {},
    )

def create_task_result(
    node_id,
    task_name,
    result=None,
    success=True,
    error=None
):
    """
    Create a task_result message.
    """

    return create_message(
        TASK_RESULT,
        node_id,
        task=task_name,
        result=result,
        success=success,
        error=error,
    )

def create_gossip_message(node_id, load):
    """
    Create a resource gossip message.
    """

    return create_message(
        GOSSIP,
        node_id,
        load=load,
    )

def create_heartbeat(node_id):
    """
    Create a heartbeat message.
    """

    return create_message(
        HEARTBEAT,
        node_id,
    )