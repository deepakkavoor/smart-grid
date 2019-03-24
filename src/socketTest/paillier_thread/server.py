# two servers at ports 10000 and 10001

import socket
import threading
import sys
sys.path.append('../../crypto/paillier/')
from paillier import *
import time

mutex = threading.Lock()

numServers = 1
numNodes = 5
numClientsPerServer = 5

PORTS = [30000 + i for i in range(numNodes)]

numClients = numNodes * numClientsPerServer
recData = [[] for _ in range(numNodes)]
sentData = []

timeSpentSending = []
timeSpentReceiving = []
timeSpentTotal = []
timeSpentEncrypting = []
timeSpentReadingKey = []
timeSpentAggregating = []
cipherLength = []

HOST = "127.0.0.1"

PORT_PARENT = 40004

def threadFunc(addressParent, addressChild, threadID):

    print("server started receiving")
    start = time.clock()

    with open("server public key.txt", "r") as keyFile:
            keys = keyFile.read().split("\n")
            pubKey = [int(key) for key in keys]

    end1 = time.clock()

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
                    
                    data = int(data)

                    recData[threadID].append(data)

    end2 = time.clock()

    result_cipher = e_add(pubKey, recData[threadID][0], recData[threadID][1]) if len(recData[threadID]) > 1 else recData[threadID][0]
    
    for i in range(2, len(recData[threadID])):
        result_cipher = e_add(pubKey, result_cipher, recData[threadID][i])

    end3 = time.clock()

    value = random.randint(0, 1000)
    sentData.append(value)
    
    mutex.acquire()
    end4 = time.clock()
    
    server_cipher = encrypt(pubKey, value)
    
    end5 = time.clock()
    mutex.release()

    result_cipher = e_add(pubKey, result_cipher, server_cipher)

    start6 = time.clock()  
    

    with socket.socket() as s:
        s.connect(addressParent)
        s.sendall(str(result_cipher).encode())


    end = time.clock()

    print("server {} sent {}".format(threadID + 1, value))

    timeSpentSending.append(end - start6)
    timeSpentReadingKey.append(end1 - start)
    timeSpentReceiving.append(end2 - end1)
    timeSpentAggregating.append(end3 - end2)
    timeSpentEncrypting.append(end5 - end4)
    timeSpentTotal.append(end - start)
    cipherLength.append(len(str(result_cipher)))


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

    print("t1 time spent reading key ", sum(timeSpentReadingKey) / len(timeSpentReadingKey))
    print("t2 time spent receiving ", sum(timeSpentReceiving) / len(timeSpentReceiving))
    print("t3 time spent aggregating ", sum(timeSpentAggregating) / len(timeSpentAggregating))
    print("t4 time spent encrypting ", sum(timeSpentEncrypting) / len(timeSpentEncrypting))
    print("t5 time spent sending ", sum(timeSpentSending) / len(timeSpentSending))
    print("t6 time spent total ", sum(timeSpentTotal) / len(timeSpentTotal))
    print("l length of message ", sum(cipherLength) / len(cipherLength))
