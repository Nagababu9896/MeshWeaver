# MeshWeaver

from dht import KademliaDHT

node_id = "a" * 64

dht = KademliaDHT(node_id)

dht.add_peer(
    "b" * 64,
    "127.0.0.1",
    9001
)

dht.add_peer(
    "c" * 64,   
    "127.0.0.1",
    9002
)

print("Total peers:", len(dht))

print("\nPeers:")

for peer in dht.get_peers():
    print(
        peer.node_id[:8],
        peer.host,
        peer.port
    )

closest = dht.find_closest_peers(
    "b" * 64,
    count=2
)

print("\nClosest peers:")

for peer in closest:
    print(peer.node_id[:8])