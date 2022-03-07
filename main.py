# TESTING OF FUNCTIONALITIES IN LOCALHOST
# MINING NODES STORING AND SENDING BY THE PEER SERVER STILL HAS TO BE IMPLEMENTED

from mining_node import MiningNode
from node import Node
import threading
import time
from peer_server import Peer_server
import json


server = Peer_server()

threading.Thread(target=server.listen).start()
server.miners_list = [('localhost',6000)]
time.sleep(1)

miner = MiningNode('localhost',6000)
threading.Thread(target=miner.listen).start()
node1 = Node()
threading.Thread(target=node1.listen).start()
node2 = Node('localhost',5000)
threading.Thread(target=node2.listen).start()
node3 = Node('localhost',5005)
threading.Thread(target=node3.listen).start()
node1.get_peers()
node2.get_peers()
miner.get_peers()

print(miner.peers)
for i in range(10):
	node1.new_transaction([('localhost',5000)],f'Transaccion numero {i}')

node4 = Node('localhost',4044)
print(json.dumps(node4.blockchain, indent=4))


node1.stop()
node2.stop()
server.stop()
miner.stop()


