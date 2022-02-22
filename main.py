
from node import Node
import threading

from peer_server import Peer_server



server = Peer_server()

threading.Thread(target=server.listen).start()

node1 = Node()
node2 = Node('localhost',5000)
node1.get_peers()

print(node1.peers)
print(node2.peers)

threading.Thread(target=node1.listen).start()
threading.Thread(target=node2.listen).start()

test_block = {
			'blocks':[
				{
					'prev_block_hash': '8cf2283ad6ef0a3266059b418a73f8479338233ea2c4bcd3c1f51c39f13ae7dc',
					'timestamp': 1645553097,
					'merkle_tree_hash':'9ca54f1c7764f74c1a1b7b75e2f92726a3506d42380e37310788f5b1721684e0',
					'extra_stuff': '0000000000',
				},
                {
                    'prev_block_hash': '96a506ca934711f901976cc70a8b573f252dbd774c8783c1ffb9a095d0392edb',
					'timestamp': 1645555390,
					'merkle_tree_hash':'9ca54f1c7764f74c1a1b7b75e2f92726a3506d42380e37310788f5b1721684e0',
					'extra_stuff': '1111111111',
                }
			]
		}

node2.blockchain = test_block

node1.request_blockchain()
server.stop()


