from __future__ import annotations
from email import message
import socket
import threading

class Node():
	def __init__(self,ip: str, port: int,peers: list[Node]) -> None:
		self.__ip = ip
		self.__port = port
		# Here you would connect to a central server to get all peers
		self.__peers : list[Node] = peers
		self.__listen : bool = True

	def send_to_all_peers(self):
		def talk_to_peer(peer: Node,msg: bytes):
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			## Connect
			sock.connect((peer.ip, peer.port))
			## Send some data, this method can be called multiple times
			sock.send(msg)

			## Receive up to 4096 bytes from a peer
			# response = sock.recv(4096)
			# print(response)
			sock.close()

		for peer in self.__peers:
			message = f'Hola soy el nodo en el puerto {self.port}'
			talk_to_peer(peer,bytes(message,'utf-8'))

		
	def listen_to_messages(self):
		self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serv.bind((self.ip, self.port))
		self.serv.listen()
		self.serv.settimeout(10)
		while self.listen:
			try:
				conn, addr = self.serv.accept()
				from_client = b''
				while True:
					data = conn.recv(4096)
					if not data: break
					from_client += data
					print(f'Server on port {self.port} received message: {str(from_client)}')
					# conn.send(b"I am SERVER\n")
					
				conn.close()
			except TimeoutError:
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
	def peers(self)-> list[Node]:
		return self.__peers
	
	@peers.setter
	def peers(self,peers):
		self.__peers = peers
	
	@listen.setter
	def listen(self,state: bool):
		self.__listen = state