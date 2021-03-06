
import socket
import json
HEADER_LENGTH = 10

class Peer_server():
	def __init__(self,hostname: str = 'localhost') -> None:
		#Here you would get the public ip addres
		self.__hostname : str = hostname
		self.__port : int = 4000
		self.__stay_listening = True
		self.__node_list = []
		self.__miners_list = []
	
	def encode_msg(self,data: dict)-> bytes:
		encoded_data = json.dumps(data)
		length = len(encoded_data)
		header = '0'*(HEADER_LENGTH-len(str(length)))+str(length)
		return header.encode('utf-8') + encoded_data.encode('utf-8')
	
	def listen(self):
		'''
            Start listening for other connections until stop() is called and timeout occurs
        '''
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
				if msg['command'] == 'request_peers':
					# Depending if its a miner or a simple node it adds them in 
					# their corresponding list if they are not alredy in there
					if msg['data'][0] == 'miner':
						if not msg['sender'] in self.__miners_list:
							self.__miners_list += [msg['sender']]
					elif msg['data'][0] == 'node':
						if not msg['sender'] in self.__node_list:
							self.__node_list += [msg['sender']]
					c.send(self.encode_msg({'data':(self.__miners_list,self.__node_list)}))
				c.close()
			except socket.timeout:
				pass

	def stop(self):
		self.__stay_listening = False
	
	@property
	def miners_list(self):
		return self.__miners_list
		
	@property
	def port(self):
		return self.__port