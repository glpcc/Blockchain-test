import hashlib
from time import time
from numpy import block
from node import Node


class MiningNode(Node):
    def __init__(self, hostname: str = 'localhost', port: int = 5555) -> None:
        super().__init__(hostname, port, True)
        # Adds special commands for mining nodes
        self.miner_msg_commands = {
            'new_transaction': self.store_transaction
        }
        self.__recent_transactions = []
        self.__mining_difficulty = 4
        self.msg_commands.update(self.miner_msg_commands)

    def store_transaction(self, args) -> str:
        '''
                Stores the transactions after verification and after 10 transactions it includes them in a mined block
        '''
        transaction = args[0]
        self.verify_transaction(transaction)
        self.__recent_transactions += [transaction]
        if len(self.__recent_transactions) >= 10:
            self.mine_block()
            self.__recent_transactions = []
        return 'ok'

    def mine_block(self) -> None:
        '''
			This function mines a block meaning it tries different 'extra stuff' until the block hash has a mining dificullty amount of 0's
		'''
        timestamp = str(time())
        transactions_hash = self.merkle_tree(self.__recent_transactions)
        prev_block_hash = self.get_block_hash(self.blockchain['blocks'][-1])
        header_without_nonce = timestamp + transactions_hash + prev_block_hash
        extra_stuff = 0
        found_hash = False
        while not found_hash:
            if hashlib.sha256((header_without_nonce + str(extra_stuff)).encode('utf-8')).hexdigest()[:self.__mining_difficulty] == '0'*self.__mining_difficulty:
                found_hash = True
                new_block = {
                    'timestamp': timestamp,
                    'prev_block_hash': prev_block_hash,
                    'merkle_tree_hash': transactions_hash,
                    'extra_stuff': extra_stuff,
                    'transactions': self.__recent_transactions

                }
                self.__recent_transactions = []
            else:
                extra_stuff += 1
            
        # Sends the mined block to all nodes for blockchain updating
        for i in self.peers:
            self.send({'command': 'new_block', 'data': [new_block]}, tuple(i)) # type: ignore
        self.blockchain['blocks'] += [new_block] # type: ignore
