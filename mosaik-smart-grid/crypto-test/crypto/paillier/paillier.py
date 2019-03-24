import math
from .primes import *
import time
import random
import time

def invmod(a, p, maxiter=1000000):
    
    if a == 0:
        raise ValueError('0 has no inverse mod %d' % p)
    r = a
    d = 1
    for i in range(min(p, maxiter)):
        d = ((p // r + 1) * d) % p
        r = (d * a) % p
        if r == 1:
            break
    else:
        raise ValueError('%d has no inverse mod %d' % (a, p))
    return d

def modpow(base, exponent, modulus):
    
    result = 1
    while exponent > 0:
        if exponent & 1 == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus
    return result


def generate_keypair(bits):
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    n = p * q

    l = (p - 1) * (q - 1)
    m = invmod(l, n)

    privKey = [l, m]

    n_sq = n * n
    g = n + 1
    pubKey = [n, n_sq, g]
    return privKey, pubKey

def encrypt(pubKey, plain):

    [n, n_sq, g] = pubKey

    while True:
        r = generate_prime(round(float(math.log(n, 2))))
        if r > 0 and r < n:
            break
    x = pow(r, n, n_sq)
    cipher = (pow(g, plain, n_sq) * x) % n_sq
    return cipher

def e_add(pubKey, a, b):

    [n, n_sq, g] = pubKey

    # return ((a % n_sq) * (b % n_sq)) % n_sq
    return (a * b) % n_sq

def e_add_const(pubKey, a, n):

    [n, n_sq, g] = pubKey

    return a * modpow(g, n, n_sq) % n_sq

def e_mul_const(pubKey, a, n):

    [n, n_sq, g] = pubKey

    return modpow(a, n, n_sq)

def decrypt(privKey, pubKey, cipher):

    [n, n_sq, g] = pubKey
    [l, m] = privKey

    x = pow(cipher, l, n_sq) - 1
    plain = ((x // n) * m) % n

    return plain

def demo():
    print("Generating keypair...")
    priv, pub = generate_keypair(256)
    print(pub)

    for _ in range(10):
        start = time.time()

        x = random.randint(0, 1000)
        cx = encrypt(pub, x)

        y = random.randint(0, 1000)
        cy = encrypt(pub, y)

        cz = e_add(pub, cx, cy)

        z = decrypt(priv, pub, cz)

        print("x, y, z ", x, y, z)
        assert z == x + y

        end = time.time()

        print("Time taken: ", end - start)

if __name__ == "__main__":
    # priv, pub = generate_keypair(512)
    demo()
    
    # for _ in range(10):
    #     start = time.time()

    #     priv, pub = generate_keypair(512)
    #     message = random.randint(10e3, 10e4)
    #     cipher = encrypt(pub, message)
    #     end = time.time()
    #     diff1 = end - start

    #     start = time.time()
    #     decoded = decrypt(priv, pub, cipher)
    #     end = time.time()
    #     diff2 = end - start

    #     print("Time for encryption: {}  Time for decryption: {}".format(diff1, diff2))
    #     assert message == decoded
