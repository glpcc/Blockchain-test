import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

## Connect to an IP with Port, could be a URL
sock.connect(('localhost', 8080))

## Send some data, this method can be called multiple times
sock.send(b"Twenty-five bytes to send")

## Receive up to 4096 bytes from a peer
response = sock.recv(4096)
print(response)
## Close the socket connection, no more data transmission
sock.close()