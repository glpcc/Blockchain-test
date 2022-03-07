
import hashlib


block = {
					'prev_block_hash': '8cf2283ad6ef0a3266059b418a73f8479338233ea2c4bcd3c1f51c39f13ae7dc',
					'timestamp': 1645553097,
					'merkle_tree_hash':'9ca54f1c7764f74c1a1b7b75e2f92726a3506d42380e37310788f5b1721684e0',
					'extra_stuff': 0000000000,
					'transactions':[
						{
							'transaction':'hello world',
							'hash':'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9',
							'signature':[]
						}
					]
				}


while True:
    if hashlib.sha256(( str(block['timestamp'])  + block['merkle_tree_hash'] + block['prev_block_hash'] + str(block['extra_stuff'])).encode('utf-8')).hexdigest()[:4] == '0'*4:
        print(hashlib.sha256(( str(block['timestamp'])  + block['merkle_tree_hash'] + block['prev_block_hash'] + str(block['extra_stuff'])).encode('utf-8')).hexdigest())
        print(block['extra_stuff'])
        break
    block['extra_stuff'] += 1
    

