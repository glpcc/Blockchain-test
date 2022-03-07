import hashlib
from time import time

from numpy import block
from node import Node
import json
import rsa


class MiningNode(Node):
	def __init__(self, hostname: str = 'localhost', port: int = 5555) -> None:
		super().__init__(hostname,port,True)
		self.miner_msg_commands = {
			'new_transaction': self.store_transaction
		}
		self.__recent_transactions = []
		self.__mining_difficulty = 4
		self.msg_commands.update(self.miner_msg_commands)



	def store_transaction(self,args):
		transaction = args[0]
		self.verify_transaction(transaction)
		self.__recent_transactions += [transaction]
		# print(json.dumps(self.__recent_transactions, indent=4))
		if len(self.__recent_transactions) >= 10:
			self.mine_block()
			self.__recent_transactions = []
		return 'ok'




	def mine_block(self) -> dict:
		timestamp = str(time())
		transactions_hash = self.merkle_tree(self.__recent_transactions)
		prev_block_hash = self.get_block_hash(self.blockchain['blocks'][-1])
		header_without_nonce = timestamp + transactions_hash + prev_block_hash
		extra_stuff = 0
		found_hash = False
		while not found_hash:
			if hashlib.sha256((header_without_nonce + str(extra_stuff)).encode('utf-8')).hexdigest()[:self.__mining_difficulty] == '0'*self.__mining_difficulty:
				found_hash = True
				print(hashlib.sha256((header_without_nonce + str(extra_stuff)).encode('utf-8')).hexdigest())
				new_block = {
					'timestamp':timestamp,
					'prev_block_hash':prev_block_hash,
					'merkle_tree_hash':transactions_hash,
					'extra_stuff':extra_stuff,
					'transactions':self.__recent_transactions
					
				}
				self.__recent_transactions = []
			else:
				extra_stuff += 1

		for i in self.peers:
			self.send({'command':'new_block','data':[new_block]},tuple(i))
		self.blockchain['blocks'] += [new_block]
	
			