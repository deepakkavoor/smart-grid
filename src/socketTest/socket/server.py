#server module

import socket

HOST = "127.0.0.1"
CLIENT_PORT = 10000
PARENT_PORT = 10001

recData = []

# with socket.socket() as s:
#     s.bind((HOST, CLIENT_PORT))
#     s.listen()
#     conn, addr = s.accept()  # addr is a tuple (HOST, PORT) of connected socket
#     with conn:
#         print("connected to client")
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             recData.append(data)
#             conn.sendall(data)

with socket.socket() as s:
    s.connect((HOST, PARENT_PORT))
    # for data in recData:
    #     s.send(data)
    #     info = s.recv(1024)
    #     print("received from parent server ", info)
    s.send(b"message from server")
    data = s.recv(1024)

print("server received data ", data)