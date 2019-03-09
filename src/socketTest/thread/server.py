# two servers at ports 10000 and 10001

import socket
import threading

numServers = 2
clientsPerServer = 2
numClients = numServers * clientsPerServer
recData = [[] for _ in range(numServers)]

HOST = "127.0.0.1"
PORT1 = 10000
PORT2 = 10001
PORT_PARENT = 10002

def threadFunc(addressParent, addressChild, threadID):
    with socket.socket() as s:
        s.bind(addressChild)
        s.listen(5)

        for _ in range(clientsPerServer):
            print("server {} is listening".format(threadID + 1))
            conn, _ = s.accept()
            with conn:
                print("connected with client")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    recData[threadID].append(int(data))

        value = sum(recData[threadID])

        with socket.socket() as s:
            s.connect(addressParent)
            s.sendall(str(value).encode())
            print("server {} sent sum {}".format(threadID + 1, value))


if __name__ == "__main__":

    server1 = threading.Thread(target = threadFunc, args = ((HOST, PORT_PARENT), (HOST, PORT1), 0,))
    server2 = threading.Thread(target = threadFunc, args = ((HOST, PORT_PARENT), (HOST, PORT2), 1,))

    server1.start()
    server2.start()

    server1.join()
    server2.join()

    print("server work done")
