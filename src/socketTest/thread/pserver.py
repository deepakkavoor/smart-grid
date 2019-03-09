# parent server

import socket

HOST = "127.0.0.1"
PORT = 10002

recData = []

with socket.socket() as s:
    s.bind((HOST, PORT))
    s.listen(10)
    for _ in range(2):
        print("parent server listening")
        conn, addr = s.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print("parent server received {} from server".format(int(data)))
                recData.append(int(data))

result = sum(recData)
print("sum at parent server is ", result)
