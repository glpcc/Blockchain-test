import socket

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serv.bind(('localhost', 8080))
serv.listen(5)

while True:
    conn, addr = serv.accept()
    from_client = b''
    
    while True:
        data = conn.recv(4096)
        if not data: break
        from_client += data
        print(str(from_client))
        conn.send(b"I am SERVER\n")
        
    conn.close()
    print('client disconnected')
    break