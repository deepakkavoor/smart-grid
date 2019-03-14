# 4 clients, 2 for each server

import socket
import threading
import random
import sys
import time
sys.path.append('../../crypto/paillier/')
from paillier import *

HOST = "127.0.0.1"


numClientsPerServer = 20
numServers = 5
PORTS = [30000 + i for i in range(numServers)]

numClients = numServers * numClientsPerServer
sentData = []
timeSpent = []

def threadFunc(address, threadID):
    with socket.socket() as s:

        print("client started sending")
        start = time.time()


        s.connect(address)
        value = random.randint(0, 10)
        sentData.append(value)

        print("client {} sent {}".format(threadID + 1, value))

        with open("server public key.txt", "r") as keyFile:
            keys = keyFile.read().split("\n")
            pubKey = [int(key) for key in keys]

        # print("keys are {} and {}".format(keys[0], keys[1])) 

        cipher = encrypt(pubKey, value)
        
        s.sendall(str(cipher).encode())


        end = time.time()
        print("finished sending in time ", end - start)
        timeSpent.append(end - start)



if __name__ == "__main__":

    clients = []
    index = 0

    for server in range(numServers):
        for client in range(numClientsPerServer):
            clients.append(threading.Thread(target = threadFunc, args = ((HOST, PORTS[server]), index,)))
            index += 1

    # client1 = threading.Thread(target = threadFunc, args = ((HOST, PORT1), 0,))
    # client2 = threading.Thread(target = threadFunc, args = ((HOST, PORT1), 1,))

    # client3 = threading.Thread(target = threadFunc, args = ((HOST, PORT2), 2,))
    # client4 = threading.Thread(target = threadFunc, args = ((HOST, PORT2), 3,))

    for client in clients:
        client.start()

    for client in clients:
        client.join()

    # client1.start()
    # client2.start()
    # client3.start()
    # client4.start()

    # client1.join()
    # client2.join()
    # client3.join()
    # client4.join()

    print("client work finished")
    print("sum of data sent by client = ", sum(sentData))