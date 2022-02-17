class Node():
	def __init__(self) -> None:
		# Here you would connect to a central server to get all peers
		self.__peers = [('localhost',8080),('localhost',8000)]

	def send_to_all_peers(self):
		