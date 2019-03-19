# two servers at ports 10000 and 10001

import socket
import threading
import sys
import time
sys.path.append('../../crypto/ECC/')
from additive_point_utils import *

mutex = threading.Lock()


numServers = 1
numNodes = 5
numClientsPerServer = 1

PORTS = [20000 + i for i in range(numNodes)]

HOST = "127.0.0.1"

PORT_PARENT = 40005

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


def threadFunc(addressParent, addressChild, threadID):

    print("server started receiving")
    start = time.clock()

    with open("server public key.txt", "r") as keyFile:
            keys = keyFile.read().split("\n")
            P_public = Point(X = int(keys[0]), Y = int(keys[1]), curve = P256)

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
                    
                    data = data.split("\n".encode())
                    data = [int(val) for val in data]

                    C = Point(X = data[0], Y = data[1], curve = P256)
                    D = Point(X = data[2], Y = data[3], curve = P256)

                    recData[threadID].append([C, D])

    end2 = time.clock()

    result_cipher = add_ciphertexts(recData[threadID][0], recData[threadID][1], P_public, Base) if len(recData[threadID]) > 1 else recData[threadID][0]
    
    for i in range(2, len(recData[threadID])):
        result_cipher = add_ciphertexts(result_cipher, recData[threadID][i], P_public, Base)

    end3 = time.clock()

    value = random.randint(0, 1000)
    sentData.append(value)

    mutex.acquire()    
    end4 = time.clock()

    server_cipher = additive_encrypt(value, P_public, Base)

    end5 = time.clock()
    mutex.release()

    result_cipher = add_ciphertexts(result_cipher, server_cipher, P_public, Base)


    start6 = time.clock()

    # print("server started sending")       

    with socket.socket() as s:
        s.connect(addressParent)
        s.sendall((  str(result_cipher[0].X) + "\n" + str(result_cipher[0].Y) + "\n" + 
        str(result_cipher[1].X) + "\n" + str(result_cipher[1].Y)  ).encode())
        print("server {} sent aggregate".format(threadID + 1))


    end = time.clock()

    # print("finished sending in time ", end - start)
    
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

    print("time spent total ", sum(timeSpentTotal) / len(timeSpentTotal))
    print("time spent reading key ", sum(timeSpentReadingKey) / len(timeSpentReadingKey))
    print("time spent aggregating ", sum(timeSpentAggregating) / len(timeSpentAggregating))
    print("time spent encrypting ", sum(timeSpentEncrypting) / len(timeSpentEncrypting))
    print("time spent sending ", sum(timeSpentSending) / len(timeSpentSending))
    print("time spent receiving ", sum(timeSpentReceiving) / len(timeSpentReceiving))
    print("length of message ", sum(cipherLength) / len(cipherLength))
