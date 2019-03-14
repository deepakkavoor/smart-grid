# two servers at ports 10000 and 10001

import socket
import threading
import sys
sys.path.append('../../crypto/paillier/')
from paillier import *
import time

numServers = 1
numNodes = 5
numClientsPerServer = 20

PORTS = [30000 + i for i in range(numNodes)]

numClients = numNodes * numClientsPerServer
recData = [[] for _ in range(numNodes)]

sentData = []
timeSpentSending = []
timeSpentReceiving = []

HOST = "127.0.0.1"

PORT_PARENT = 40004

def threadFunc(addressParent, addressChild, threadID):

    print("server started receiving")
    start = time.time()

    with open("server public key.txt", "r") as keyFile:
            keys = keyFile.read().split("\n")
            pubKey = [int(key) for key in keys]

    with socket.socket() as s:
        s.bind(addressChild)
        s.listen(21)

        for _ in range(numClientsPerServer):
            # print("server {} is listening".format(threadID + 1))
            conn, _ = s.accept()
            with conn:
                # print("connected with client")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    data = int(data)

                    recData[threadID].append(data)

        result_cipher = e_add(pubKey, recData[threadID][0], recData[threadID][1])
        
        for i in range(2, len(recData[threadID])):
            result_cipher = e_add(pubKey, result_cipher, recData[threadID][i])


        value = random.randint(0, 10)
        sentData.append(value)
        print("server {} sent {}".format(threadID + 1, value))

        server_cipher = encrypt(pubKey, value)

        result_cipher = e_add(pubKey, result_cipher, server_cipher)


        end = time.time()
        print("finished receiving in ", end - start, " s")
        timeSpentReceiving.append(end - start)

        print("server started sending")
        start = time.time()  
        

        with socket.socket() as s:
            s.connect(addressParent)
            s.sendall(str(result_cipher).encode())
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
