# https://github.com/RyanRiddle/elgamal/blob/master/elgamal.py

import random
import math

class PrivateKey:
    def __init__(self, p = None, g = None, x = None, iNumBits = 0):
        self.p = p
        self.g = g
        self.x = x
        self.iNumBits = iNumBits


class PublicKey:
    def __init__(self, p = None, g = None, h = None, iNumBits = 0):
        self.p = p
        self.g = g
        self.h = h
        self.iNumBits = iNumBits


def gcd(a, b):
    while b != 0:
        a, b = b, a % b

    return a


def modexp(base, exp, modulus):
    return pow(base, exp, modulus)


def findRandNum(iNumBits):
    return random.randint( 2 ** (iNumBits - 2), 2 ** (iNumBits - 1) - 1)


def findPrime(iNumBits, iConfidence):
    while True:
        p = findRandNum(iNumBits)

        while p % 2 == 0:
            p = findRandNum(iNumBits)

        while solovayStrassen(p, iConfidence) == False:
            p = findRandNum(iNumBits)

            while p % 2 == 0:
                p = findRandNum(iNumBits)

        p = 2 * p + 1

        if solovayStrassen(p, iConfidence) == True:
            return p


def solovayStrassen(num, iConfidence):
    for _ in range(iConfidence):
        a = random.randint(1, num - 2)

        if gcd(a, num) > 1:
            return False

        if not ( jacobi(a, num) % num == modexp(a, (num - 1)//2, num) ):
            return False

    return True


def jacobi(a, n):
    if a == 0:
        if n == 1:
            return 1
        else:
            return 0

    elif a == -1:
        if n % 2 == 0:
            return 1
        else:
            return -1

    elif a == 1:
        return 1

    elif a == 2:
        if n % 8 == 1 or n % 8 == 7:
            return 1
        elif n % 8 == 3 or n % 8 == 5:
            return -1

    elif a >= n:
        return jacobi(a % n, n)

    elif a % 2 == 0:
        return jacobi(2, n) * jacobi(a // 2, n)

    else:
        if a % 4 == 3 and n % 4 == 3:
            return -1 * jacobi(n, a)
        else:
            return jacobi(n, a)


def findPrimitiveRoot(p):
    if p == 2:
        return 1

    div1 = 2
    div2 = (p - 1) // 2

    while(True):
        g = random.randint(2, p - 2)

        if modexp( g, (p - 1) // div1, p) != 1 and modexp( g, (p - 1) // div2, p) != 1:
            return g


def generateKeys(iNumBits = 256, iConfidence = 32):
    p = findPrime(iNumBits, iConfidence)
    
    g = modexp( findPrimitiveRoot(p), 2, p)

    x = random.randint(1, (p - 1) // 2 - 1)

    h = modexp(g, x, p)

    publicKey = PublicKey(p, g, h, iNumBits)
    privateKey = PrivateKey(p, g, x, iNumBits)

    return {'privateKey': privateKey, 'publicKey': publicKey}


def encrypt(key, message):
    y = random.randint(0, key.p - 1)

    c = modexp(key.g, y, key.p)

    d = ( message * modexp(key.h, y, key.p) ) % key.p

    cipher_pair = [c, d]
    return cipher_pair


def decrypt(key, cipher_pair):
    c, d = cipher_pair

    s = modexp(c, key.x, key.p)

    message = ( d * modexp(s, key.p - 2, key.p) ) % key.p

    return message


def test():
    keys = generateKeys()
    message = random.randint(0, 10e5)
    cipher = encrypt(keys['publicKey'], message)
    plain = decrypt(keys['privateKey'], cipher)

    print(message == plain)

if __name__ == '__main__':
    for _ in range(10):
        test()
