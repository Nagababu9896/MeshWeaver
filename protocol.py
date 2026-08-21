# MeshWea
import json

class ProtocolError(Exception):
    pass

VALID_TYPES = {
    "PING",
    "PONG",
    "JOIN",
    "JOIN_RESPONSE",
    "GOSSIP",
    "HEARTBEAT",
    "HEARTBEAT_ACK",
    "TASK_REQUEST",
    "TASK_RESULT",
    "TASK_FAILED",
}

def create_message(message_type: str, sender: str, **payload):
    if message_type not in VALID_TYPES:
        raise ProtocolError(
            f"Unknown message type: {message_type}"
        )

    message = {
        "type": message_type,
        "sender": sender,
        "payload": payload,
    }

    return json.dumps(message).encode("utf-8")

def parse_message(data: bytes):
    try:
        message = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("Invalid JSON message") from exc

    if not isinstance(message, dict):
        raise ProtocolError("Message must be an object")

    if "type" not in message:
        raise ProtocolError("Missing message type")

    if "sender" not in message:
        raise ProtocolError("Missing sender")

    if "payload" not in message:
        message["payload"] = {}

    if message["type"] not in VALID_TYPES:
        raise ProtocolError(
            f"Unsupported message type: {message['type']}"
        )

    return message

