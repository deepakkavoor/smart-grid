# 4 clients, 2 for each server

import socket
import threading
import random
import sys
import time
sys.path.append('../../crypto/paillier/')
from paillier import *

HOST = "127.0.0.1"

mutex = threading.Lock()

numClientsPerServer = 5
numServers = 5
PORTS = [30000 + i for i in range(numServers)]

numClients = numServers * numClientsPerServer
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
            pubKey = [int(key) for key in keys]

        mutex.acquire()
        end1 = time.clock()

        cipher = encrypt(pubKey, value)
        
        end2 = time.clock()
        mutex.release()

        s.sendall(str(cipher).encode())


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

    # print("time spent total ", sum(timeSpentTotal) / len(timeSpentTotal))
    # print("time spent reading key ", sum(timeSpentReadingKey) / len(timeSpentReadingKey))
    # print("time spent encrypting ", sum(timeSpentEncrypting) / len(timeSpentEncrypting))
    # print("time spent sending ", sum(timeSpentSending) / len(timeSpentSending))
    # print("length of message ", sum(cipherLength) / len(cipherLength))