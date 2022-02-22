import json
import socket

HEADER_LENGTH = 10

class Node():
	def __init__(self,hostname: str = 'localhost',port: int = 5555) -> None:
		#Here you would get the public ip addres
		self.__hostname : str = hostname
		self.__port : int = port
		self.__peer_server = ('localhost',4000)
		self.__peers : list[tuple[str,int]] = []
		self.get_peers()
		self.__stay_listening = True
		self.__MSG_COMMANDS = {

		}

	def encode_msg(self,data: dict)-> bytes:
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


	def get_peers(self):
		self.__peers += [ i for i in self.send({'command':'request_peers','data':'','sender':(self.__hostname,self.__port)},self.__peer_server)['data'] if not i in self.__peers and i != [self.__hostname,self.__port]]

	def listen(self):
		HEADER_LENGTH = 10
		s = socket.socket()
		s.bind(('', self.__port))
		s.listen(5) 
		while True:
			c, addr = s.accept()
			msg_lenght = int(c.recv(HEADER_LENGTH).decode('utf-8'))
			msg = c.recv(msg_lenght)
			print(json.loads(msg))
			c.send('Thank ou for connecting'.encode())
			c.close()
			break

	@property 
	def peers(self):
		return self.__peers