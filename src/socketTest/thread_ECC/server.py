# two servers at ports 10000 and 10001

import socket
import threading
import sys
sys.path.append('../../crypto/ECC/')
from additive_point_utils import *

numServers = 2
clientsPerServer = 2
numClients = numServers * clientsPerServer
recData = [[] for _ in range(numServers)]

HOST = "127.0.0.1"
PORT1 = 10002
PORT2 = 10003
PORT_PARENT = 10005

def threadFunc(addressParent, addressChild, threadID):

    with open("server public key.txt", "r") as keyFile:
            keys = keyFile.read().split("\n")
            P_public = Point(X = int(keys[0]), Y = int(keys[1]), curve = P256)

    with socket.socket() as s:
        s.bind(addressChild)
        s.listen(5)

        for _ in range(clientsPerServer):
            # print("server {} is listening".format(threadID + 1))
            conn, _ = s.accept()
            with conn:
                # print("connected with client")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    data = data.split("\n".encode())
                    data = [int(val) for val in data]

                    C = Point(X = data[0], Y = data[1], curve = P256)
                    D = Point(X = data[2], Y = data[3], curve = P256)

                    recData[threadID].append([C, D])

        result_cipher = add_ciphertexts(recData[threadID][0], recData[threadID][1], P_public, Base)

        value = random.randint(0, 10)
        print("server {} sent {}".format(threadID + 1, value))

        server_cipher = additive_encrypt(value, P_public, Base)

        result_cipher = add_ciphertexts(result_cipher, server_cipher, P_public, Base)
        

        with socket.socket() as s:
            s.connect(addressParent)
            s.sendall((  str(result_cipher[0].X) + "\n" + str(result_cipher[0].Y) + "\n" + 
            str(result_cipher[1].X) + "\n" + str(result_cipher[1].Y)  ).encode())
            print("server {} sent aggregate".format(threadID + 1))


if __name__ == "__main__":

    server1 = threading.Thread(target = threadFunc, args = ((HOST, PORT_PARENT), (HOST, PORT1), 0,))
    server2 = threading.Thread(target = threadFunc, args = ((HOST, PORT_PARENT), (HOST, PORT2), 1,))

    server1.start()
    server2.start()

    server1.join()
    server2.join()

    print("server work done")
