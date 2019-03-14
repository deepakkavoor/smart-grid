# two servers at ports 10000 and 10001

import socket
import threading
import sys
import time
sys.path.append('../../crypto/ECC/')
from additive_point_utils import *


numServers = 1
numNodes = 10
numClientsPerServer = 20

PORTS = [20000 + i for i in range(numNodes)]

numClients = numNodes * numClientsPerServer
recData = [[] for _ in range(numNodes)]

sentData = []
timeSpentSending = []
timeSpentReceiving = []

HOST = "127.0.0.1"

PORT_PARENT = 10005

def threadFunc(addressParent, addressChild, threadID):

    print("server started receiving")
    start = time.time()

    with open("server public key.txt", "r") as keyFile:
            keys = keyFile.read().split("\n")
            P_public = Point(X = int(keys[0]), Y = int(keys[1]), curve = P256)

    with socket.socket() as s:
        s.bind(addressChild)
        s.listen()

        for _ in range(numClientsPerServer):
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
        
        for i in range(2, len(recData[threadID])):
            result_cipher = add_ciphertexts(result_cipher, recData[threadID][i], P_public, Base)


        value = random.randint(0, 10)
        sentData.append(value)
        print("server {} sent {}".format(threadID + 1, value))

        server_cipher = additive_encrypt(value, P_public, Base)

        result_cipher = add_ciphertexts(result_cipher, server_cipher, P_public, Base)


        end = time.time()
        print("finished receiving in ", end - start, " s")
        timeSpentReceiving.append(end - start)

        print("server started sending")
        start = time.time()        

        with socket.socket() as s:
            s.connect(addressParent)
            s.sendall((  str(result_cipher[0].X) + "\n" + str(result_cipher[0].Y) + "\n" + 
            str(result_cipher[1].X) + "\n" + str(result_cipher[1].Y)  ).encode())
            print("server {} sent aggregate".format(threadID + 1))


        end = time.time()
        print("finished receiving in time ", end - start)
        timeSpentSending.append(end - start)


if __name__ == "__main__":

    nodes = []
    index = 0

    for node in range(numNodes):
        nodes.append(threading.Thread(target = threadFunc, args = ((HOST, PORT_PARENT), (HOST, PORTS[index]), index, )))
        index += 1

    for node in nodes:
        node.start()

    for node in nodes:
        node.join()

    print("server work done")
    print("sum of data sent by server = ", sum(sentData))
