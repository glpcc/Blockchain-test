#!/usr/bin/python

from multiprocessing import Pool
import hashlib

DIFICULTY = 8

def test_hashes(num):
	test_num = num*10**8
	not_found = True

	end_test_num = test_num + 10**8
	while not_found and test_num <= end_test_num:
		if hashlib.sha256(str(test_num).encode('utf-8')).hexdigest()[:DIFICULTY] == '0'*DIFICULTY:
			print(hashlib.sha256(str(test_num).encode('utf-8')).hexdigest())
			print(test_num)
			not_found = False
		elif test_num % 1000000 == 0:
			print(f'Tried till number:{test_num} ')
		test_num += 1

def main():

    p = Pool(7)		
    p.map(test_hashes,[i for i in range(7)])

if __name__ == '__main__':
    main()

 