from .point_utils import *

def additive_encrypt(message, P_public, Base):
    # https://nvotes.com/multiplicative-vs-additive-homomorphic-elgamal/

    k = random.randint(1, Base.curve.P - 1)

    C1 = pointMultiply(Base, k)
    temp1 = pointMultiply(P_public, k)
    temp2 = pointMultiply(Base, message)
    C2 = pointAdd(temp1, temp2)
    cipher = [C1, C2]

    return cipher

def compute_table(Base):
    size = 2001
    start = time.time()
    table = {}
    for i in range(0, size):
        table[pointMultiply(Base, i).getX()] = i

    end = time.time()
    print("Time to build table of {} elements: ".format(size), end - start)
    return table

def additive_decrypt(cipher, privateKey, Base, table):
    [C, D] = cipher

    C_ = pointMultiply(C, privateKey)
    plain = pointSubtract(D, C_)
    
    if plain.getX() not in table:
        print("Unable to decrypt. Message too long")
        return

    return table[plain.getX()]

def add_ciphertexts(cipher1, cipher2, P_public, Base):
    [A, B] = cipher1
    [C, D] = cipher2

    result = [pointAdd(A, C), pointAdd(B, D)]
    
    return result

def randomize(cipher, P_public, Base):
    zero = additive_encrypt(0, P_public, Base)
    return add_ciphertexts(cipher, zero, P_public, Base)

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

if __name__ == "__main__":
    print("Computing table")
    table = compute_table(Base)
    print("Finished table generation")

    for _ in range(10):
        start = time.time()

        privateKey = random.randint(1, P256.P - 1)
        P_public = pointMultiply(Base, privateKey)

        x = random.randint(0, 1000)
        y = random.randint(0, 1000)

        cipher_x = additive_encrypt(x, P_public, Base)
        cipher_y = additive_encrypt(y, P_public, Base)

        cipher_z = add_ciphertexts(cipher_x, cipher_y, P_public, Base)

        # randomize(cipher_z, P_public, Base)

        z = additive_decrypt(cipher_z, privateKey, Base, table)

        print("x, y, z ", x, y, z)
        assert z == x + y

        end = time.time()
        print("Time spent: ", end - start)
