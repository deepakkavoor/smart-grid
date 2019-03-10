from .point import Point

class Curve:
    # https://github.com/AntonKueltz/fastecdsa/blob/master/fastecdsa/curve.self.Py

    def __init__(self, name, P, A, B, Q, Gx, Gy):
        self.name = name
        self.P = P
        self.A = A
        self.B = B
        self.Q = Q
        self.Gx = Gx
        self.Gy = Gy

    def PointOnCurve(self, P1):
        X, Y = P1.getX(), P1.getY()

        left = (Y * Y) % self.P
        right = ( ((X * X) % self.P) * X) % self.P + (self.A * X) % self.P + self.B

        return (left - right) % self.P == 0

    def evaluate(self, X):
        right = ( ((X * X) % self.P) * X) % self.P + (self.A * X) % self.P + self.B

        return right % self.P 

    def __repr__(self):
        return self.name

    def G(self):
        return Point(self.Gx, self.Gy, self)


"""
P256 = Curve(
    'P256',
    115792089210356248762697446949407573530086143415290314195533631308867097853951,
    -3,
    41058363725152142129326129780047268409114441015993725554835256314039467401291,
    115792089210356248762697446949407573529996955224135760342422259061068512044369,
    48439561293906451759052585252797914202762949526041747995844080717082404635286,
    36134250956749795798585127919587881956611106672985015071877198253568414405109,
    b'\x2A\x86\x48\xCE\x3D\x03\x01\x07'
)
"""