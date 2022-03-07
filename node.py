from __future__ import annotations

import rsa
import hashlib
import json
import random
import socket
from errors.incorrect_block import Incorrect_Block
from errors.incorrect_blockchain import Incorrect_Blockchain
from errors.signature_failure import Signature_failure

HEADER_LENGTH = 10

class Node():
	def __init__(self,hostname: str = 'localhost',port: int = 5555,try_peers = True) -> None:
		#Here you would get the public ip addres
		self.__hostname : str = hostname
		self.__port : int = port
		self.__peer_server = ('localhost',4000)
		self.__peers : list[tuple[str,int]] = []
		self.__mining_nodes : list[tuple[str,int]] = []
		self.__mining_difficulty = 4
		# here you could ask the peers for other peers
		try:
			if try_peers:
				self.get_peers()
		except:
			print('The connection to the peer server wasnt possible')
		self.__stay_listening = True
		self.__blockchain = {
			'blocks':[
				{
					'prev_block_hash': '8cf2283ad6ef0a3266059b418a73f8479338233ea2c4bcd3c1f51c39f13ae7dc',
					'timestamp': 1645553097,
					'merkle_tree_hash':'9ca54f1c7764f74c1a1b7b75e2f92726a3506d42380e37310788f5b1721684e0',
					'extra_stuff': 25241,
					'transactions':[]
				},
			]

		}
		self.request_blockchain()

		self.__msg_commands = {
			'request_blockchain':self.send_blockchain,
			'request_signature': self.sign_transaction,
			'request_publickey': self.send_publickey,
			'new_block':self.add_new_block
		}
		
		# Generate public key and private key for validating transactions
		self.__public_key, self.__private_key = rsa.newkeys(512)


	def send_publickey(self,args):
		return self.__public_key.save_pkcs1().decode('utf-8')


	def get_block_hash(self,block: dict):
		return hashlib.sha256(( str(block['timestamp'])  + block['merkle_tree_hash'] + block['prev_block_hash'] + str(block['extra_stuff'])).encode('utf-8')).hexdigest()

	def send_blockchain(self,args):
		return self.__blockchain

	def request_blockchain(self):
		if len(self.__peers) > 0:
			chosen_peer = random.choice(self.__peers)
			print(chosen_peer)
			temp_blockchain = self.send({'command':'request_blockchain','data':[]},tuple(chosen_peer))
			#Here i check if the blockchain is correct
			
			if len(temp_blockchain['blocks']) > 0:
				print('hey')
				founded = False
				while not founded:
					try:
						self.verify_blockchain(temp_blockchain)
						print(json.dumps(temp_blockchain, indent=4))
						print('Foundeeeed')
						founded = True
						self.__blockchain = temp_blockchain
					except Exception as e:
						print('Mala blockchain')
						chosen_peer = random.choice(self.__peers)
						temp_blockchain = self.send({'command':'request_blockchain','data':[]},tuple(chosen_peer))

	def add_new_block(self,args):
		block = args[0]
		try:
			self.verify_block(block,verify_transactions=True,check_mktree=True)
			self.__blockchain['blocks'] += [block]
			return 'ok'
		except Incorrect_Block or Incorrect_Blockchain or rsa.VerificationError:
			print('Erroooor')
			return 'invalid_block'


	def verify_transaction(self,transaction):
		for signature in transaction['signatures']:
			if signature['node'] == [self.__hostname,self.__port]:
				rsa.verify(transaction['transaction'].encode('utf-8'),bytes.fromhex(signature['firm']),self.__public_key)
			else:
				peer_pubkey = rsa.PublicKey.load_pkcs1(self.send({'command':'request_publickey','data':[]},tuple(signature['node'])).encode('utf-8'))
				rsa.verify(transaction['transaction'].encode('utf-8'),bytes.fromhex(signature['firm']),peer_pubkey)


	def merkle_tree(self,transactions):

		# This will make a merkle tree hash of thre transactions
		transaction_hashes = []
		for i in transactions:
			transaction_hashes += [i['hash']]
		
		while len(transaction_hashes) > 1:
			new_t_hashes = []
			for i in range(0,len(transaction_hashes),2):
				try:
					new_t_hashes += [hashlib.sha256((transaction_hashes[i]+transaction_hashes[i+1]).encode('utf-8')).hexdigest()]
				except IndexError:
					new_t_hashes += [transaction_hashes[i]]			
			transaction_hashes = new_t_hashes
		return transaction_hashes[0]

	
	def verify_blockchain(self,blockchain):
		if len(blockchain['blocks']) > 1:
			for i in range(1,len(blockchain['blocks'])):
				if blockchain['blocks'][i]['prev_block_hash'] != self.get_block_hash(blockchain['blocks'][i-1]):
					raise Incorrect_Blockchain
				else:
					self.verify_block(blockchain['blocks'][i])
		else:
			if blockchain['blocks'][0]['prev_block_hash'] != '8cf2283ad6ef0a3266059b418a73f8479338233ea2c4bcd3c1f51c39f13ae7dc':
				raise Incorrect_Blockchain
			else:
				self.verify_block(blockchain['blocks'][0])

	
	def verify_block(self,block,check_mktree: bool = False,verify_transactions: bool = False,verify_block_hash: bool = True):
		if check_mktree:
			if self.merkle_tree(block['transactions']) != block['merkle_tree_hash']:
				raise Incorrect_Block
		if verify_transactions:
			for transaction in block['transactions']:
				self.verify_transaction(transaction)
		if verify_block_hash:
			if self.get_block_hash(block)[:self.__mining_difficulty] != '0'*self.__mining_difficulty:
				raise Incorrect_Block



	def encode_msg(self,data)-> bytes:
		encoded_data = json.dumps(data)
		length = len(encoded_data)
		header = '0'*(HEADER_LENGTH-len(str(length)))+str(length)
		return header.encode('utf-8') + encoded_data.encode('utf-8')

	def send(self,data: dict,peer: tuple[str,int]):
		
		s = socket.socket() 
		s.connect(peer)
		s.send(self.encode_msg(data))
		msg_lenght = int(s.recv(HEADER_LENGTH).decode('utf-8'))
		msg = s.recv(msg_lenght)
		msg = json.loads(msg)
		s.close()
		return msg

	def sign(self,data :bytes) -> bytes:
		return rsa.sign(data,self.__private_key,'SHA-256')

	def new_transaction(self,other_peers_implicated : list[tuple[str, int]],transaction: str):

		final_transaction = {
			'transaction':transaction,
			'hash':hashlib.sha256(transaction.encode('utf-8')).hexdigest(),
			'signatures':[]
		}
		final_transaction['signatures'] += [{'node':(self.__hostname,self.__port),'firm':self.sign(transaction.encode('utf-8')).hex()}]
		# Now send the encrypted hash to all other nodes implied in transaction for signing
		for node in other_peers_implicated:
			data = {
				'command':'request_signature',
				'data':[transaction]
			}
			sign = self.send(data,node)['data']
			if sign == 'no':
				raise Signature_failure('One of the nodes refused to sign the transaction')
			final_transaction['signatures'] += [{'node':node,'firm':sign}]

		data_to_send = {
			'command':'new_transaction',
			'data':[final_transaction]
		}
		for i in self.__mining_nodes:
			self.send(data_to_send,i)
		
	def get_peers(self):
		mining_nodes, peers = self.send({'command':'request_peers','data':'','sender':(self.__hostname,self.__port)},self.__peer_server)['data']
		self.__peers += [ i for i in peers if not i in self.__peers and i != [self.__hostname,self.__port]]
		self.__mining_nodes += [tuple(i) for i in mining_nodes if not tuple(i) in self.__mining_nodes]

	def sign_transaction(self,args):
		transaction : str = args[0]
		rs = input(f'Do you want to sign this transaction: {transaction} \n (y/n):')
		if rs == 'y':
			return {'data':self.sign(transaction.encode('utf-8')).hex()}
		else:
			return {'data':'no'}


	def listen(self):
		print(f'Node in port {self.__port} started listening')
		s = socket.socket()
		s.bind(('', self.__port))
		s.listen(5)
		s.settimeout(5)
		while self.__stay_listening:
			try:
				c, addr = s.accept()
				msg_lenght = int(c.recv(HEADER_LENGTH).decode('utf-8'))
				msg = c.recv(msg_lenght)
				msg = json.loads(msg)
				c.send(self.encode_msg(self.__msg_commands[msg['command']](msg['data'])))
				c.close()
			except socket.timeout:
				pass

	def stop(self):
		print(f'Node on port {self.__port} stoped listening')
		self.__stay_listening = False


	@property 
	def peers(self):
		return self.__peers
	
	@property 
	def mining_nodes(self):
		return self.__mining_nodes

	@property
	def msg_commands(self):
		return self.__msg_commands

	#TODO remove
	@property
	def blockchain(self):
		return self.__blockchain
	
	@msg_commands.setter
	def msg_commands(self,cmd):
		self.__msg_commands = cmd
	@blockchain.setter
	def blockchain(self,blockchai):
		self.__blockchain = blockchai