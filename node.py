from __future__ import annotations
from numpy import block
import rsa
import hashlib
import json
import random
import socket
import typing
from errors.incorrect_block import Incorrect_Block
from errors.incorrect_blockchain import Incorrect_Blockchain
from errors.signature_failure import Signature_failure

HEADER_LENGTH = 10

# types for legibility
Blockchain = dict[str, list[dict]]
Block = dict
Hex = str


class Node():
    def __init__(self, hostname: str = 'localhost', port: int = 5555, try_peers=True) -> None:
        # Assigns the passed hostname and port
        self.__hostname: str = hostname
        self.__port: int = port
        # Here you can change the peer server to call
        self.__peer_server = ('localhost', 4000)
        # initialize peer list and miner list
        self.__peers: list[tuple[str, int]] = []
        self.__mining_nodes: list[tuple[str, int]] = []
        # Sets mining dificulty for know it is constant
        self.__mining_difficulty = 4
        # Asks the peer server for the peer list
        try:
            if try_peers:
                self.get_peers()
        except:
            print('The connection to the peer server wasnt possible')
        # Here you could ask the peers for other peers
        #
        self.__stay_listening = True
        # Initialize the blockchain with the standar first block
        self.__blockchain: Blockchain = {
            'blocks': [
                {
                    'prev_block_hash': '8cf2283ad6ef0a3266059b418a73f8479338233ea2c4bcd3c1f51c39f13ae7dc',
                    'timestamp': 1645553097,
                    'merkle_tree_hash': '9ca54f1c7764f74c1a1b7b75e2f92726a3506d42380e37310788f5b1721684e0',
                    'extra_stuff': 25241,
                    'transactions': []
                },
            ]

        }
        # Request others peers for newer blockchains
        self.request_blockchain()
        # A list of the communications commands
        self.__msg_commands = {
            'request_blockchain': self.send_blockchain,
            'request_signature': self.sign_transaction,
            'request_publickey': self.send_publickey,
            'new_block': self.add_new_block
        }
        # Generate public key and private key for validating transactions
        self.__public_key, self.__private_key = rsa.newkeys(512)

    def send_publickey(self, args) -> str:
        '''
                Returns the node's publickey in string format
        '''
        return self.__public_key.save_pkcs1().decode('utf-8')

    def get_block_hash(self, block: Block) -> Hex:
        '''
                Hashes the block with and returns it in hex format
                block_hash = sha256(timestamp + merkle tree hash + previous block hash + extra stuff)
        '''
        return hashlib.sha256((str(block['timestamp']) + block['merkle_tree_hash'] + block['prev_block_hash'] + str(block['extra_stuff'])).encode('utf-8')).hexdigest()

    def send_blockchain(self, args) -> Blockchain:
        '''
                Returns the nodes stored blockchain
        '''
        return self.__blockchain

    def request_blockchain(self) -> None:
        '''
                Selects random peers to request their stored blockchain and repeats until one of the blockchains is valid
        '''
        if len(self.__peers) > 0:
            # Selects a peer from the stored list of peers
            chosen_peer = random.choice(self.__peers)
            # Requests the blockchain
            temp_blockchain = self.send(
                {'command': 'request_blockchain', 'data': []}, tuple(chosen_peer))
            # Here checks if the blockchain is correct
            if len(temp_blockchain['blocks']) > 0:
                founded = False
                while not founded:
                    try:
                        # Checks the blockchain and if no error occurs it asigns it to it's stored blockchain
                        self.verify_blockchain(temp_blockchain)
                        founded = True
                        self.__blockchain = temp_blockchain
                    except (Incorrect_Block, Incorrect_Blockchain, rsa.VerificationError) as e:
                        # If an error occurs it chooses another random peer and tries again
                        chosen_peer = random.choice(self.__peers)
                        temp_blockchain = self.send(
                            {'command': 'request_blockchain', 'data': []}, tuple(chosen_peer))

    def add_new_block(self, args) -> str:
        '''
                Receives a new block from a miner and after verification it adds it to its blockchain
        '''
        block = args[0]
        try:
            self.verify_block(
                block, verify_transactions=True, check_mktree=True)
            self.__blockchain['blocks'] += [block]
            return 'Ok'
        except (Incorrect_Block, Incorrect_Blockchain, rsa.VerificationError) as e:
            return 'invalid_block'

    def verify_transaction(self, transaction) -> None:
        '''
            Verifies if a transaction was signed by all the participants and raises an error if it wasn't
            signed by that node
        '''
        for signature in transaction['signatures']:
            # if the one to verify is the node doing the verification it checks with its own public key
            if signature['node'] == [self.__hostname, self.__port]:
                rsa.verify(transaction['transaction'].encode(
                    'utf-8'), bytes.fromhex(signature['firm']), self.__public_key)
            # if its another node it requests it's public key
            else:
                peer_pubkey = rsa.PublicKey.load_pkcs1(self.send(
                    {'command': 'request_publickey', 'data': []}, tuple(signature['node'])).encode('utf-8'))
                rsa.verify(transaction['transaction'].encode(
                    'utf-8'), bytes.fromhex(signature['firm']), peer_pubkey)  # type: ignore

    def merkle_tree(self, transactions) -> Hex:
        '''
                This function implement the merkle tree algorithm to hash a list of transactions
                In this implementations the odd remaining hashes are left to the next iteration until they can be hashed with another one
                Source: https://en.wikipedia.org/wiki/Merkle_tree
        '''
        # Gets the hashes of the transactions
        transaction_hashes = []
        for i in transactions:
            transaction_hashes += [i['hash']]
        # Apply the algorithm
        while len(transaction_hashes) > 1:
            new_t_hashes = []
            for i in range(0, len(transaction_hashes), 2):
                try:
                    new_t_hashes += [hashlib.sha256(
                        (transaction_hashes[i]+transaction_hashes[i+1]).encode('utf-8')).hexdigest()]
                except IndexError:
                    new_t_hashes += [transaction_hashes[i]]
            transaction_hashes = new_t_hashes
        # Returns the final hash
        return transaction_hashes[0]

    def verify_blockchain(self, blockchain: Blockchain) -> None:
        '''
            This function checks an entire blockchain for incorrect previous hashes or incorrect blocks and raises an error it that happens
        '''	
        # Checks the first block prev hash with the default one
        if blockchain['blocks'][0]['prev_block_hash'] != '8cf2283ad6ef0a3266059b418a73f8479338233ea2c4bcd3c1f51c39f13ae7dc':
                raise Incorrect_Blockchain
        else:
            self.verify_block(blockchain['blocks'][0])
            for i in range(1, len(blockchain['blocks'])):
                if blockchain['blocks'][i]['prev_block_hash'] != self.get_block_hash(blockchain['blocks'][i-1]):
                    raise Incorrect_Blockchain
                else:
                    self.verify_block(blockchain['blocks'][i])

    def verify_block(self, block: Block, check_mktree: bool = False, verify_transactions: bool = False, verify_block_hash: bool = True)-> None:
        '''
            Checks optionally three parts of a blockchain block
                - merkle tree
                    - It check if the merkle tree hash of the block transactions is equal to the one written in the block
                        and raises Incorrect_Block exception if not
                - Transactions
                    - Verifies if all transactions where firmed by all the nodes involved. It raises rca.VerificationError if it wasn't
                - Block Hash
                    - Verifies if the total block hash satisfies the given block difficulty (If it was mined or not) and raises Incorrect_Block if not
        '''
        if check_mktree:
            if self.merkle_tree(block['transactions']) != block['merkle_tree_hash']:
                raise Incorrect_Block
        if verify_transactions:
            for transaction in block['transactions']:
                self.verify_transaction(transaction)
        if verify_block_hash:
            if self.get_block_hash(block)[:self.__mining_difficulty] != '0'*self.__mining_difficulty:
                raise Incorrect_Block

    def encode_msg(self, data) -> bytes:
        '''
            Encodes some json formatable data to json str, adds the header with the message length and returns it in byte form
        '''
        encoded_data = json.dumps(data)
        length = len(encoded_data)
        header = '0'*(HEADER_LENGTH-len(str(length)))+str(length)
        return header.encode('utf-8') + encoded_data.encode('utf-8')

    def send(self, data: dict, peer: tuple):
        '''
            Sends some data to a given peer, the data should be in format
            {
                'command': the command to do with the data
                'data': the data to send
            }
        '''
        s = socket.socket()
        s.connect(peer)
        s.send(self.encode_msg(data))
        # Decodes the message to return the response
        msg_lenght = int(s.recv(HEADER_LENGTH).decode('utf-8'))
        msg = s.recv(msg_lenght)
        msg = json.loads(msg)
        s.close()
        # Returns the response
        return msg

    def sign(self, data: bytes) -> bytes:
        '''
            Signs a given data with the nodes private key
        '''
        return rsa.sign(data, self.__private_key, 'SHA-256')

    def new_transaction(self, other_peers_implicated: list[tuple[str, int]], transaction: str)-> None:
        '''
            This function starts a new transaction an after getting it signed by all the peers involved it sends it to the miner nodes
        '''
        final_transaction = {
            'transaction': transaction,
            'hash': hashlib.sha256(transaction.encode('utf-8')).hexdigest(),
            'signatures': []
        }
        # Sign the transaction itself
        final_transaction['signatures'] += [{'node': (
            self.__hostname, self.__port), 'firm': self.sign(transaction.encode('utf-8')).hex()}]
        # Now send the transaction to all other nodes implied in transaction for singing
        for node in other_peers_implicated:
            data = {
                'command': 'request_signature',
                'data': [transaction]
            }
            sign = self.send(data, node)['data']
            if sign == 'no':
                raise Signature_failure('One of the nodes refused to sign the transaction')
            final_transaction['signatures'] += [{'node': node, 'firm': sign}]

        data_to_send = {
            'command': 'new_transaction',
            'data': [final_transaction]
        }
        # Send the transaction to al the mining nodes
        for i in self.__mining_nodes:
            self.send(data_to_send, i)

    def get_peers(self)-> None:
        '''
            Gets peers and mining nodes from the peer server if it doesn't have them alredy
        '''
        mining_nodes, peers = self.send({'command': 'request_peers', 'data': '', 'sender': (self.__hostname, self.__port)}, self.__peer_server)['data']
        self.__peers += [i for i in peers if not i in self.__peers and i !=
                         [self.__hostname, self.__port]]
        self.__mining_nodes += [tuple(i)
                                for i in mining_nodes if not tuple(i) in self.__mining_nodes]

    def sign_transaction(self, args)-> dict:
        '''
            Asks the Node user if it wants to sign the incoming transaction
        '''
        transaction: str = args[0]
        rs = input(
            f'Do you want to sign this transaction: {transaction} \n (y/n):')
        if rs == 'y':
            return {'data': self.sign(transaction.encode('utf-8')).hex()}
        else:
            return {'data': 'no'}

    def listen(self):
        '''
            Start listening for other connections until stop() is called and timeout occurs
        '''
        print(f'Node in port {self.__port} started listening')
        s = socket.socket()
        s.bind(('', self.__port))
        s.listen(5)
        s.settimeout(5)
        while self.__stay_listening:
            try:
                c, addr = s.accept()
                # Decodes the header to know the message length and then receive it
                msg_lenght = int(c.recv(HEADER_LENGTH).decode('utf-8'))
                msg = c.recv(msg_lenght)
                msg = json.loads(msg)
                c.send(self.encode_msg(
                    self.__msg_commands[msg['command']](msg['data'])))
                c.close()
            except socket.timeout:
                pass

    def stop(self):
        '''
            Stops the node from listening
        '''
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

    @property
    def blockchain(self):
        return self.__blockchain

    @msg_commands.setter
    def msg_commands(self, cmd):
        self.__msg_commands = cmd

    @blockchain.setter
    def blockchain(self, blockchai):
        self.__blockchain = blockchai
