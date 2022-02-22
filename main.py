
from node import Node
import threading

from peer_server import Peer_server



server = Peer_server()

threading.Thread(target=server.listen).start()

node1 = Node()
node2 = Node('localhost',5000)
node1.get_peers()

print(node1.peers)
print(node2.peers)
server.stop()

