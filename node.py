from __future__ import annotations

import rsa
import hashlib
import json
import random
import socket

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
					'extra_stuff': '0000000000',
				},
			]

		}
		self.__msg_commands = {
			'request_blockchain':self.send_blockchain,
			'request_signature': self.sign_transaction,
			'request_publickey': self.send_publickey,
		}
		
		# Generate public key and private key for validating transactions
		self.__public_key, self.__private_key = rsa.newkeys(512)


	def send_publickey(self,args):
		return self.__public_key.save_pkcs1().decode('utf-8')


	def get_block_hash(self,block: dict):
		return hashlib.sha256((block['prev_block_hash']+ str(block['timestamp']) + block['merkle_tree_hash'] + str(block['extra_stuff'])).encode('utf-8')).hexdigest()

	def send_blockchain(self,args):
		block_header_hash = args[0]
		for i in range(len(self.__blockchain['blocks'])):
			if self.get_block_hash(self.__blockchain['blocks'][i]) == block_header_hash:
				print(i)
				return {'blocks': self.__blockchain['blocks'][i+1:]}
		return self.__blockchain

	def request_blockchain(self):
		chosen_peer = random.choice(self.__peers)
		print(chosen_peer)
		temp_blockchain = self.send({'command':'request_blockchain','data':(self.get_block_hash(self.__blockchain['blocks'][-1]))},tuple(chosen_peer))
		print(temp_blockchain)

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