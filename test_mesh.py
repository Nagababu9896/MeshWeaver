# MeshWeaver

from copy import deepcopy

from dht import KademliaDHT
from registry import create_default_registry
from security import MessageSecurity


def test_dht():
    dht = KademliaDHT("a" * 64)

    dht.add_peer("b" * 64, "127.0.0.1", 8001)
    dht.add_peer("c" * 64, "127.0.0.1", 8002)

    assert len(dht) == 2

    closest = dht.find_closest_peers("b" * 64)
    assert closest
    assert closest[0].node_id == "b" * 64

    print("DHT test: PASS")


def test_registry():
    registry = create_default_registry()

    assert registry.execute("add", [10, 20]) == 30
    assert registry.execute("multiply", [5, 4]) == 20
    assert registry.execute("square", [6]) == 36

    print("Registry test: PASS")


def test_security():
    security = MessageSecurity("meshweaver-secret")

    message = {
        "type": "PING",
        "node_id": "node001",
    }

    secured = security.secure_message(message)

    assert security.verify_message(secured), "Original message failed verification"

    tampered = deepcopy(secured)

    if not isinstance(tampered, dict):
        raise TypeError("secure_message() must return a dictionary")

    if isinstance(tampered.get("message"), dict):
        tampered["message"]["node_id"] = "attacker"
    elif isinstance(tampered.get("payload"), dict):
        tampered["payload"]["node_id"] = "attacker"
    elif "node_id" in tampered:
        tampered["node_id"] = "attacker"
    else:
        raise KeyError("Could not find node_id in secured message")

    assert not security.verify_message(tampered), "Tampered message was accepted"

    print("Security test: PASS")


def test_protocol():
    import protocol

    message = protocol.create_ping("node001")

    assert protocol.validate_message(message)

    encoded = protocol.encode_message(message)
    decoded = protocol.decode_message(encoded)

    assert decoded["type"] == protocol.PING
    assert decoded["node_id"] == "node001"

    print("Protocol test: PASS")


def run_tests():
    print("=" * 50)
    print("MeshWeaver Integration Tests")
    print("=" * 50)

    test_dht()
    test_registry()
    test_security()
    test_protocol()

    print("=" * 50)
    print("ALL TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    run_tests()