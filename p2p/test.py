from math import fabs
from platform import node
from node import Node
import threading

nodes: list[Node]= [Node('localhost',8000,[]),Node('localhost',8001,[]),Node('localhost',8002,[])]
for i in nodes:
	i.peers = [j for j in nodes if j != i]

threading.Thread(target=nodes[0].listen_to_messages, args=()).start()
threading.Thread(target=nodes[1].listen_to_messages, args=()).start()
threading.Thread(target=nodes[2].listen_to_messages, args=()).start()

nodes[0].send_to_all_peers()
nodes[2].send_to_all_peers()

for i in nodes:
	i.stop()



