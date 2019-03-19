# parent server

import socket
import sys
sys.path.append('../../crypto/paillier/')
from paillier import *
import time

HOST = "127.0.0.1"
PORT = 40004
numClients = 10

recData = []

timeSpentTotal = []
timeSpentGeneratingKey = []
timeSpentReceiving = []
timeSpentAggregating = []
timeSpentDecrypting = []

def decrypt_data(P_public):
    print("start decrypting aggregated data")
    start = time.clock()


    with socket.socket() as s:
        s.bind((HOST, PORT))
        s.listen()
        for _ in range(numClients):
            # print("parent server listening")
            conn, _ = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    # print("parent server received data from server")
                    
                    data = int(data)

                    recData.append(data)

    end1 = time.clock()

    result_cipher = e_add(pubKey, recData[0], recData[1]) if len(recData) > 1 else recData[0]        
    for i in range(2, len(recData)):
        result_cipher = e_add(pubKey, result_cipher, recData[i])

    end2 = time.clock()
    
    result = decrypt(privKey, pubKey, result_cipher)

    end = time.clock()
    
    print("parent server obtained sum ", result)
    timeSpentTotal.append(end - start)
    timeSpentAggregating.append(end2 - end1)
    timeSpentDecrypting.append(end - end2)
    timeSpentReceiving.append(end1 - start)



if __name__ == "__main__":

    print("Generating keypair...")

    start5 = time.clock()
    privKey, pubKey = generate_keypair(256)
    end5 = time.clock()


    with open("server public key.txt", "w") as keyFile:
        keyFile.write(str(pubKey[0]) + "\n" + str(pubKey[1]) + "\n" + str(pubKey[2]))

    decrypt_data(pubKey)

    print("time spent generating key ", end5 - start5)
    print("time spent total ", sum(timeSpentTotal) / len(timeSpentTotal))
    print("time spent decrypting ", sum(timeSpentDecrypting) / len(timeSpentDecrypting))
    print("time spent receiving ", sum(timeSpentReceiving) / len(timeSpentReceiving))
    print("time spent aggregating ", sum(timeSpentAggregating) / len(timeSpentAggregating))
