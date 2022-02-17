from __future__ import annotations
import hashlib
import time


class Block():
	def __init__(self,info : list,prev_hash) -> None:
		self.__info: list = info
		self.__time_stamp : float = time.time()
		self.__block_mark : str = str(info) + prev_hash.hexdigest() + str(self.__time_stamp)
		self.__hash = hashlib.sha512(self.__block_mark.encode())

	@property 
	def hash(self):
		return self.__hash
	

