import hashlib
from time import time
from node import Node
import json


class MiningNode(Node):
	def __init__(self, hostname: str = 'localhost', port: int = 5555) -> None:
		super().__init__(hostname, port)
		self.miner_msg_commands = {
			'new_transaction': self.store_transaction
		}
		self.__recent_transactions = []
		self.miner_msg_commands.update(self.msg_commands)
		self.__mining_difficulty = 4
	
	def store_transaction(self,transaction):
		self.__recent_transactions += [transaction]
		if len(self.__recent_transactions) >= 10:
			print(json.dumps(self.mine_block(), indent=4))
		
	def mine_block(self) -> dict:
		timestamp = str(time())
		transactions_hash = self.hash_transactions()
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
					'transactions':[self.__recent_transactions]
					
				}
				self.__recent_transactions = []
			else:
				extra_stuff += 1
		return new_block
	
	def hash_transactions(self) -> str:
		# This will make a merkle tree hash of thre transactions
		transaction_hashes = [i['hash'] for i in self.__recent_transactions]
		while len(transaction_hashes) > 1:
			new_t_hashes = []
			for i in range(0,len(transaction_hashes),2):
				try:
					new_t_hashes += [hashlib.sha256((transaction_hashes[i]+transaction_hashes[i+1]).encode('utf-8')).hexdigest()]
				except IndexError:
					new_t_hashes += [transaction_hashes[i]]			
			transaction_hashes = new_t_hashes
		return transaction_hashes[0]
			