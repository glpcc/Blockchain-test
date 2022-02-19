
from node import Node
import threading
import pickle
from message import Message

nodes: list[Node]= [Node('localhost',8000,[]),Node('localhost',8001,[]),Node('localhost',8002,[])]
for i in nodes:
	i.peers = [(j.ip,j.port) for j in nodes if j != i]



threading.Thread(target=nodes[0].listen_to_messages, args=()).start()
threading.Thread(target=nodes[1].listen_to_messages, args=()).start()
threading.Thread(target=nodes[2].listen_to_messages, args=()).start()

threading.Thread(nodes[0].get_main_blockchain())

for i in nodes:
	i.stop()



