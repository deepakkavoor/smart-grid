# parent server

import socket
import sys
sys.path.append('../../crypto/ECC/')
from additive_point_utils import *

HOST = "127.0.0.1"
PORT = 40005
numClients = 10

recData = []
timeSpent = []

table = compute_table(Base)

def decrypt_data(P_public):
    print("start decrypting aggregated data")
    start = time.time()

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

        result_cipher = add_ciphertexts(recData[0], recData[1], P_public, Base)
        
        for i in range(2, len(recData)):
            result_cipher = add_ciphertexts(result_cipher, recData[i], P_public, Base)
        
        
        result = additive_decrypt(result_cipher, privateKey, Base, table)
        print("parent server obtained sum ", result)

        end = time.time()
        print("finished in time ", end - start, " s")
        timeSpent.append(end - start)


if __name__ == "__main__":

    privateKey = random.randint(1, P256.P - 1)
    P_public = pointMultiply(Base, privateKey)

    with open("server public key.txt", "w") as keyFile:
        keyFile.write(str(P_public.getX()) + "\n" + str(P_public.getY()))

    decrypt_data(P_public)
