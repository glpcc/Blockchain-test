
from mining_node import MiningNode
from node import Node
import threading
import time
from peer_server import Peer_server



server = Peer_server()

threading.Thread(target=server.listen).start()
server.miners_list = [('localhost',6000)]
time.sleep(1)

miner = MiningNode('localhost',6000)
node1 = Node()
node2 = Node('localhost',5000)
node3 = Node('localhost',5005)
node1.get_peers()
node2.get_peers()

threading.Thread(target=node1.listen).start()
threading.Thread(target=node2.listen).start()
threading.Thread(target=node3.listen).start()
threading.Thread(target=miner.listen).start()

for i in range(10):
	node1.new_transaction([('localhost',5000),('localhost',5005)],f'Transaccion numero {i}')


node1.stop()
node2.stop()
server.stop()
miner.stop()


