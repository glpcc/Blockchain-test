
from demo_controler import Demo_Controller


cont = Demo_Controller()

running = True
options = 'Press a number for one of the next actions\n 0 -> End Demo \n 1 -> Add New Node \n 2 -> Add new miner \n 3 -> Make new transaction \n 4 -> Mine new block \n 5 -> Show blockchain stored on a certain node'
while running:
    print(options)
    r = input('Select your option: ')
    if r == '0':
        cont.stop_all()
        running = False
    elif r == '1':
        port = input('Select a port for the Node: ')
        cont.add_node(int(port))
    elif r == '2':
        port = input('Select a port for the Miner: ')
        cont.add_miner(int(port))
    elif r == '3':
        nodes_indexes = input('Introduce the index of the nodes involved separated with comas: ').split(',')
        transaction = input('Introduce the content of the transaction')
        cont.create_new_transction([int(i) for i in nodes_indexes],transaction)
    elif r == '4':
        cont.mine_block()
    elif r == '5': 
        n_index = int(input('Introduce the index of the node: '))
        cont.show_blockchain(n_index)
