# parent server

import socket
import sys
sys.path.append('../../crypto/ECC/')
from additive_point_utils import *

HOST = "127.0.0.1"
PORT = 40005
numClients = 5

recData = []

timeSpentTotal = []
timeSpentGeneratingKey = []
timeSpentReceiving = []
timeSpentAggregating = []
timeSpentDecrypting = []

table = compute_table(Base, 0, 10000)

def decrypt_data(P_public):
    print("start decrypting aggregated data")
    start = time.clock()

    with socket.socket() as s:
        s.bind((HOST, PORT))
        s.listen()
        for _ in range(numClients):
            print("parent server listening")
            conn, _ = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print("parent server received data from server")
                    
                    data = data.split("\n".encode())
                    data = [int(val) for val in data]

                    C = Point(X = data[0], Y = data[1], curve = P256)
                    D = Point(X = data[2], Y = data[3], curve = P256)

                    recData.append([C, D])

    end1 = time.clock()

    result_cipher = add_ciphertexts(recData[0], recData[1], P_public, Base) if len(recData) > 1 else recData[0]
    
    for i in range(2, len(recData)):
        result_cipher = add_ciphertexts(result_cipher, recData[i], P_public, Base)
    
    end2 = time.clock()
    
    result = additive_decrypt(result_cipher, privateKey, Base, table)
    # print("parent server obtained sum ", result)

    end = time.clock()
    # print("finished in time ", end - start, " s")

    print("parent server obtained sum ", result)
    timeSpentTotal.append(end - start)
    timeSpentAggregating.append(end2 - end1)
    timeSpentDecrypting.append(end - end2)
    timeSpentReceiving.append(end1 - start)
 

if __name__ == "__main__":

    start5 = time.clock()

    privateKey = random.randint(1, P256.P - 1)
    P_public = pointMultiply(Base, privateKey)

    end5 = time.clock()

    with open("server public key.txt", "w") as keyFile:
        keyFile.write(str(P_public.getX()) + "\n" + str(P_public.getY()))

    decrypt_data(P_public)

    print("time spent generating key ", end5 - start5)
    print("time spent total ", sum(timeSpentTotal) / len(timeSpentTotal))
    print("time spent decrypting ", sum(timeSpentDecrypting) / len(timeSpentDecrypting))
    print("time spent receiving ", sum(timeSpentReceiving) / len(timeSpentReceiving))
    print("time spent aggregating ", sum(timeSpentAggregating) / len(timeSpentAggregating))
