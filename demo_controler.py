import json
from mining_node import MiningNode
from node import Node
from peer_server import Peer_server
import threading


def foo(x):
	x.mine_block

class Demo_Controller():
	def __init__(self) -> None:
		self.nodes : list[Node] = []
		self.peer_server : Peer_server = Peer_server()
		threading.Thread(target=self.peer_server.listen).start()
		self.miners : list[MiningNode] = []
	
	def add_node(self,port):
		if all((port != i.port for i in self.nodes)) and all((port != i.port for i in self.miners)) and port != self.peer_server.port:
			self.nodes += [Node('localhost',port)]
			threading.Thread(target=self.nodes[-1].listen).start()
		else:
			print(f'Port number: {port} is alredy in use, retry with another one')
	
	def add_miner(self,port):
		if all((port != i.port for i in self.nodes)) and all((port != i.port for i in self.miners)) and port != self.peer_server.port:
			self.miners += [MiningNode('localhost',port)]
			threading.Thread(target=self.miners[-1].listen).start()
		else:
			print(f'Port number: {port} is alredy in use, retry with another one')
	
	def create_new_transction(self,nodes_involved_indexes: list[int],transaction_message: str):
		if self.nodes != []:
			nodes_involved = [(i.hostname,i.port) for i in [self.nodes[j] for j in nodes_involved_indexes[1:]]]
			print(f'hola: {nodes_involved}')
			self.nodes[nodes_involved_indexes[0]].new_transaction(nodes_involved,transaction_message)
		else:
			print('You havent made any nodes')
	def mine_block(self):
		'''	
			This will force the mining of a new block might lead to problems with race conditions if mining dificulty is below 6
		'''
		if self.miners != []:
			mining_threads = []
			for i in self.miners:
				mining_threads += [threading.Thread(target=i.mine_block)]
				mining_threads[-1].start()
			
			for i in mining_threads:
				i.join()
		else:
			print('You haven`t created any nodes')
		

		
	
	def show_blockchain(self,node_index : int = 0):
		try:
			print(json.dumps(self.nodes[node_index].blockchain, indent=4))
		except IndexError:
			print(f'Theres no node at position {node_index}')

	def stop_all(self):
		self.peer_server.stop()
		for i in self.nodes:
			i.stop()
		for i in self.miners:
			i.stop()