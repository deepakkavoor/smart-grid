from .point import Point
from .curve import Curve
import random
import time

class CurveMismatchError(Exception):
    def __init__(self, curve1, curve2):
        self.msg = 'Tried to add points on two different curves <{}> & <{}>'.format(
            curve1.name, curve2.name)

def extendedGCD(a, b):
    # https://rosettacode.org/wiki/Modular_inverse#Python
    # https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm#Iterative_method_2

    lastremainder, remainder = abs(a), abs(b)
    x, lastx, y, lasty = 0, 1, 1, 0
    
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(lastremainder, remainder)
        x, lastx = lastx - quotient*x, x
        y, lasty = lasty - quotient*y, y
    
    return lastremainder, lastx * (-1 if a < 0 else 1), lasty * (-1 if b < 0 else 1)

def modInverse(a, m):
    g, x, _ = extendedGCD(a, m)
	
    if g != 1:
        raise ValueError
	
    return x % m

def pointAdd(P1, P2):
    # https://andrea.corbellini.name/2015/05/17/elliptic-curve-cryptography-a-gentle-introduction/

    if P1.getX() == 0 and P1.getY() == 0:
        return P2
    
    if P2.getX() == 0 and P2.getY() == 0:
        return P1

    if P1.curve is not P2.curve:
        raise CurveMismatchError(P1.curve, P2.curve)

    if P1.getY() - P2.getY() == 0:
        return Point(0, 0)

    if P1.getX() == P2.getX():
        return pointDouble(P1)

    
    P = P1.curve.P
    slope = (P1.getY() - P2.getY()) % P
    inv = modInverse(P1.getX() - P2.getX(), P)
    slope = (slope * inv) % P

    newX = ((slope * slope) % P - P1.getX() - P2.getX() + P) % P

    # note change in sign, since P + Q = -R
    newY = (-P1.getY() - (slope * (newX - P1.getX())) % P + P) % P

    return Point(newX, newY, P1.curve) 



def pointInverse(P1):
    newX = P1.getX()
    newY = -P1.getY()

    return Point(newX, newY % P1.curve.P, P1.curve)   


def pointDouble(P1):
    if P1.getX() == 0 and P1.getY() == 0:
        return Point(0, 0)

    P = P1.curve.P
    A = P1.curve.A
    X = P1.getX()
    Y = P1.getY()

    slope = ((3 * X * X) % P + A) % P
    inv = modInverse(2 * Y, P)
    slope = (slope * inv) % P

    newX = ((slope * slope) % P - (2 * X) % P + P) % P

    # note change in sign, since P + P = -R
    newY = (-Y - (slope * (newX - X)) % P + P) % P

    if newY < 0:
        newY = newY + P

    return Point(newX, newY, P1.curve)

def pointSubtract(P1, P2):
    return pointAdd(P1, pointInverse(P2))

def bits(n):
    while(n):
        yield n & 1
        n = n >> 1

def pointMultiply(P1, n):
    # https://andrea.corbellini.name/2015/05/17/elliptic-curve-cryptography-a-gentle-introduction/

    if n < 0:
        raise NotImplementedError

    result = Point(0, 0, P1.curve)
    addend = P1
    for bit in bits(n):
        if bit == 1:
            result = pointAdd(result, addend)
        addend = pointDouble(addend)

    return result

def encrypt(Pm, P_public, Base):
    # https://crypto.stackexchange.com/questions/9987/elgamal-with-elliptic-curves

    k = random.randint(1, Base.curve.P - 1)
    
    C1 = pointMultiply(Base, k)
    temp = pointMultiply(P_public, k)
    C2 = pointAdd(Pm, temp)
    cipher = [C1, C2]

    return cipher 

def decrypt(cipher, privateKey, Base):
    [C, D] = cipher

    C_ = pointMultiply(C, privateKey)
    Pm = pointSubtract(D, C_)

    return Pm


if __name__ == "__main__":
    P256 = Curve(
        'P256',
        115792089210356248762697446949407573530086143415290314195533631308867097853951,
        -3,
        41058363725152142129326129780047268409114441015993725554835256314039467401291,
        115792089210356248762697446949407573529996955224135760342422259061068512044369,
        48439561293906451759052585252797914202762949526041747995844080717082404635286,
        36134250956749795798585127919587881956611106672985015071877198253568414405109,
    )

    Base = P256.G()

    privateKey = random.randint(1, P256.P - 1)
    P_public = pointMultiply(Base, privateKey)
    
    # for _ in range(10):
    #     start = time.time()

    #     privateKey = random.randint(1, P256.P - 1)
    #     P_public = pointMultiply(Base, privateKey)
        
    #     message = random.randint(10e50, 10e60)
    #     Pm = Point(message, P256.evaluate(message), P256)
    #     cipher = encrypt(Pm, P_public, Base)

    #     end = time.time()
    #     diff1 = end - start

    #     start = time.time()
    #     new_Pm = decrypt(cipher, privateKey, Base)
        
    #     end = time.time()
    #     diff2 = end - start

    #     print("Time for encryption: {}  Time for decryption: {}".format(diff1, diff2))

    #     print(Pm.getX() == new_Pm.getX() and Pm.getY() == new_Pm.getY())
    #     # print(Pm, new_Pm)

    







