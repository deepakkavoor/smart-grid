# client module

import socket

HOST = "127.0.0.1"
PORT = 10001

with socket.socket() as s:
    s.connect((HOST, PORT))
    s.send(b"message from client")
    data = s.recv(1024)

print("client received data ", data)