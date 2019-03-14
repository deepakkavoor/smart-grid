# parent server

import socket
import sys
sys.path.append('../../crypto/paillier/')
from paillier import *

HOST = "127.0.0.1"
PORT = 20005

recData = []

def decrypt_data(P_public):
    with socket.socket() as s:
        s.bind((HOST, PORT))
        s.listen(10)
        for _ in range(2):
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
        
        result = decrypt(privKey, pubKey, result_cipher)
        print("parent server obtained sum ", result)


if __name__ == "__main__":

    print("Generating keypair...")
    privKey, pubKey = generate_keypair(256)

    with open("server public key.txt", "w") as keyFile:
        keyFile.write(str(pubKey[0]) + "\n" + str(pubKey[1]) + "\n" + str(pubKey[2]))

    decrypt_data(pubKey)
