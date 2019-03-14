# 4 clients, 2 for each server

import socket
import threading
import random
import sys
import time
sys.path.append('../../crypto/ECC/')
from additive_point_utils import *

HOST = "127.0.0.1"

numClientPerServer = 20
numServers = 10

PORTS = [20000 + i for i in range(numServers)]

numClients = numServers * numClientPerServer
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
            P_public = Point(X = int(keys[0]), Y = int(keys[1]), curve = P256)

        #print("keys are {} and {}".format(keys[0], keys[1])) 

        cipher = additive_encrypt(value, P_public, Base)

        s.sendall((  str(cipher[0].X) + "\n" + str(cipher[0].Y) + "\n" + 
            str(cipher[1].X) + "\n" + str(cipher[1].Y)  ).encode())

        
        end = time.time()
        print("finished sending in time ", end - start)
        timeSpent.append(end - start)


if __name__ == "__main__":

    clients = []
    index = 0

    for server in range(numServers):
        for client in range(numClientPerServer):
            clients.append(threading.Thread(target = threadFunc, args = ((HOST, PORTS[server]), index,)))
            index += 1

    for client in clients:
        client.start()

    for client in clients:
        client.join()

    print("client work finished")
    print("sum of data sent by client = ", sum(sentData))