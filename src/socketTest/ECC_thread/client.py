# 4 clients, 2 for each server

import socket
import threading
import random
import sys
import time
sys.path.append('../../crypto/ECC/')
from additive_point_utils import *

HOST = "127.0.0.1"

mutex = threading.Lock()

numClientPerServer = 5
numServers = 5

PORTS = [50000 + i for i in range(numServers)]

numClients = numServers * numClientPerServer
sentData = []

timeSpentTotal = []
timeSpentEncrypting = []
timeSpentReadingKey = []
timeSpentSending = []
cipherLength = []

def threadFunc(address, threadID):
    with socket.socket() as s:

        print("client started sending")
        start = time.clock()


        s.connect(address)
        value = random.randint(0, 1000)
        sentData.append(value)

        start1 = time.clock()

        with open("server public key.txt", "r") as keyFile:
            keys = keyFile.read().split("\n")
            P_public = Point(X = int(keys[0]), Y = int(keys[1]), curve = P256)

        mutex.acquire()
        end1 = time.clock() 

        cipher = additive_encrypt(value, P_public, Base)

        end2 = time.clock()
        mutex.release()

        s.sendall((  str(cipher[0].X) + "\n" + str(cipher[0].Y) + "\n" + 
            str(cipher[1].X) + "\n" + str(cipher[1].Y)  ).encode())

        
    end = time.clock()
    print("client {} sent {}".format(threadID + 1, value))
    # print("finished sending in time ", end - start)

    timeSpentTotal.append(end - start)
    timeSpentReadingKey.append(end1 - start1)
    timeSpentEncrypting.append(end2 - end1)
    timeSpentSending.append(end - end2)
    cipherLength.append(len(str(cipher)))


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

    # print("time spent total ", sum(timeSpentTotal) / len(timeSpentTotal))
    # print("time spent reading key ", sum(timeSpentReadingKey) / len(timeSpentReadingKey))
    # print("time spent encrypting ", sum(timeSpentEncrypting) / len(timeSpentEncrypting))
    # print("time spent sending ", sum(timeSpentSending) / len(timeSpentSending))
    # print("length of message ", sum(cipherLength) / len(cipherLength))