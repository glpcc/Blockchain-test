import hashlib
from mining_node import MiningNode
import random

m = MiningNode()
transactions = [
	{
		'hash': 'b221d9dbb083a7f33428d7c2a3c3198ae925614d70210e28716ccaa7cd4ddb79'
	},
	{
		'hash': 'aaa9402664f1a41f40ebbc52c9993eb66aeb366602958fdfaa283b71e64db123'
	},
	{
		'hash': 'bcb6fe9ddcc2799d676f9a7e2865e68c633d8e324af27af8d4888b50cc356083'
	}
]


for i in range(10):
	m.store_transaction(random.choice(transactions))