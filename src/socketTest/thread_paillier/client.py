# 4 clients, 2 for each server

import socket
import threading
import random
from paillier.paillier import *

HOST = "127.0.0.1"
PORT1 = 20002
PORT2 = 20003

numClients = 4

def threadFunc(address, threadID):
    with socket.socket() as s:
        s.connect(address)
        value = random.randint(0, 10)

        print("client {} sent {}".format(threadID + 1, value))

        with open("server public key.txt", "r") as keyFile:
            keys = keyFile.read().split("\n")
            pubKey = [int(key) for key in keys]

        #print("keys are {} and {}".format(keys[0], keys[1])) 

        cipher =encrypt(pubKey, value)

        s.sendall(str(cipher).encode())



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