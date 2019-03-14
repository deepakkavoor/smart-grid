# 4 clients, 2 for each server

import socket
import threading
import random
import sys
import time
sys.path.append('../../crypto/ECC/')
from additive_point_utils import *

HOST = "127.0.0.1"
PORT1 = 10002
PORT2 = 10003

numClients = 4

def threadFunc(address, threadID):
    with socket.socket() as s:
        s.connect(address)
        value = random.randint(0, 10)

        print("client {} sent {}".format(threadID + 1, value))

        with open("server public key.txt", "r") as keyFile:
            keys = keyFile.read().split("\n")
            P_public = Point(X = int(keys[0]), Y = int(keys[1]), curve = P256)

        #print("keys are {} and {}".format(keys[0], keys[1])) 

        cipher = additive_encrypt(value, P_public, Base)

        s.sendall((  str(cipher[0].X) + "\n" + str(cipher[0].Y) + "\n" + 
            str(cipher[1].X) + "\n" + str(cipher[1].Y)  ).encode())



if __name__ == "__main__":
    client1 = threading.Thread(target = threadFunc, args = ((HOST, PORT1), 0,))
    client2 = threading.Thread(target = threadFunc, args = ((HOST, PORT1), 1,))

    client3 = threading.Thread(target = threadFunc, args = ((HOST, PORT2), 2,))
    client4 = threading.Thread(target = threadFunc, args = ((HOST, PORT2), 3,))

    client1.start()
    client2.start()
    client3.start()
    client4.start()

    client1.join()
    client2.join()
    client3.join()
    client4.join()

    print("client work finished")