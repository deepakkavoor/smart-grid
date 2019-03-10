# two servers at ports 10000 and 10001

import socket
import threading
from paillier.paillier import *

numServers = 2
clientsPerServer = 2
numClients = numServers * clientsPerServer
recData = [[] for _ in range(numServers)]

HOST = "127.0.0.1"
PORT1 = 20002
PORT2 = 20003
PORT_PARENT = 20005

def threadFunc(addressParent, addressChild, threadID):

    with open("server public key.txt", "r") as keyFile:
            keys = keyFile.read().split("\n")
            pubKey = [int(key) for key in keys]

    with socket.socket() as s:
        s.bind(addressChild)
        s.listen(5)

        for _ in range(clientsPerServer):
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

        # result = decrypt(privKey, pubKey, result_cipher)
        # print("server obtained sum ", result)

        value = random.randint(0, 10)
        print("server {} sent {}".format(threadID + 1, value))

        server_cipher = encrypt(pubKey, value)

        result_cipher = e_add(pubKey, result_cipher, server_cipher)
        

        with socket.socket() as s:
            s.connect(addressParent)
            s.sendall(str(result_cipher).encode())
            print("server {} sent aggregate".format(threadID + 1))


if __name__ == "__main__":

    # print("Generating keypair...")
    # privKey, pubKey = generate_keypair(256)

    # with open("server public key.txt", "w") as keyFile:
    #     keyFile.write(str(pubKey[0]) + "\n" + str(pubKey[1]) + "\n" + str(pubKey[2]))

    server1 = threading.Thread(target = threadFunc, args = ((HOST, PORT_PARENT), (HOST, PORT1), 0,))
    server2 = threading.Thread(target = threadFunc, args = ((HOST, PORT_PARENT), (HOST, PORT2), 1,))

    server1.start()
    server2.start()

    server1.join()
    server2.join()

    print("server work done")
