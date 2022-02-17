from block import Block
import hashlib

class BlockChain():
	def __init__(self,chain: list[Block] = []) -> None:
		if chain != []:
			self.__chain = [chain[0]]
		else:
			self.__chain = [Block([hashlib.sha512(''.encode())],hashlib.sha512(''.encode()))]

	def new_block(self,new_info: list) -> None:
		self.__chain += [Block(new_info,self.__chain[-1].hash)]
		
