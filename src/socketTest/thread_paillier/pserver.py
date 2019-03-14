# parent server

import socket
import sys
sys.path.append('../../crypto/paillier/')
from paillier import *
import time

HOST = "127.0.0.1"
PORT = 40004
numClients = 5

recData = []
timeSpent = []

def decrypt_data(P_public):
    print("start decrypting aggregated data")
    start = time.time()


    with socket.socket() as s:
        s.bind((HOST, PORT))
        s.listen(11)
        for _ in range(numClients):
            print("parent server listening")
            conn, _ = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print("parent server received data from server")
                    
                    data = int(data)

                    recData.append(data)

        result_cipher = e_add(pubKey, recData[0], recData[1])
        for i in range(2, len(recData)):
            result_cipher = e_add(pubKey, result_cipher, recData[i])
        
        result = decrypt(privKey, pubKey, result_cipher)
        print("parent server obtained sum ", result)

        end = time.time()
        print("finished in time ", end - start, " s")
        timeSpent.append(end - start)


if __name__ == "__main__":

    print("Generating keypair...")
    privKey, pubKey = generate_keypair(256)

    with open("server public key.txt", "w") as keyFile:
        keyFile.write(str(pubKey[0]) + "\n" + str(pubKey[1]) + "\n" + str(pubKey[2]))

    decrypt_data(pubKey)
