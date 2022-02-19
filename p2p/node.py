from __future__ import annotations
import socket
import pickle
import threading
import time
from message import	Message

class Node():
	def __init__(self, ip: str, port: int, peers: list[tuple[str,int]]) -> None:
		self.__ip = ip
		self.__port = port
		# Here you would connect to a central server to get all peers
		self.__peers: list[tuple[str,int]] = peers
		self.__listen: bool = True
		self.__recent_data = []

	def send_to_all_peers(self, msg: bytes):
		# TODO consider adding threading here if posible
		for peer in self.__peers:
			self.send_to_peer(peer, msg)

	def send_to_peer(self, peer: tuple[str,int], msg: bytes):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((peer[0], peer[1]))
		sock.send(msg)
		# Receive up to 4096 bytes from a peer
		# response = sock.recv(4096)
		# print(response)

		sock.close()

	def get_main_blockchain(self):
		self.send_to_all_peers(pickle.dumps(Message('request_blockchain','',self.__port)))
		while len(self.__recent_data) != len(self.__peers):
			time.sleep(0.5)
		
		# test
		print(self.__recent_data)

	def listen_to_messages(self):
		self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serv.bind((self.ip, self.port))
		self.serv.listen()
		self.serv.settimeout(5)
		while self.listen:
			try:
				conn, addr = self.serv.accept()
				raw_data: bytes = bytes()
				while True:
					data = conn.recv(4096)
					if not data: break
					raw_data += data
				message = pickle.loads(raw_data)
				if message.command == 'test':
					print(message.sender)
					print(message.data.a)
				elif message.command == 'request_blockchain':
					msg = f'Blockchain del nodo en el puerto {self.__port}'
					print(addr)
					self.send_to_peer((addr[0],message.sender),pickle.dumps(Message('response',msg.encode('utf-8'),self.__port)))
				elif message.command == 'response':
					self.__recent_data += [message.data]
				conn.close()
			except TimeoutError:
				pass
			except socket.timeout:
				pass
		print(f'Server on port {self.port} stoped listening')

	def __str__(self) -> str:
		return f'Node with ip:{self.ip} and port:{self.port}'

	def stop(self):
		self.listen = False

	@property
	def ip(self)-> str:
		return self.__ip

	@property
	def port(self)-> int:
		return self.__port 

	@property
	def listen(self)-> bool:
		return self.__listen 

	@property
	def peers(self)-> list[tuple[str,int]]:
		return self.__peers
	
	@peers.setter
	def peers(self,peers):
		self.__peers = peers
	
	@listen.setter
	def listen(self,state: bool):
		self.__listen = state
