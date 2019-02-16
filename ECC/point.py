class Point:

    def __init__(self, X = 0, Y = 0, curve = None):
        self.X = X
        self.Y = Y
        self.curve = curve

    def getX(self):
        return self.X

    def getY(self):
        return self.Y  

    def setX(self, X):
        self.X = X

    def setY(self, Y):
        self.Y = Y

    def __str__(self):
        return "X: " + str(self.X) + "  " + "Y: " + str(self.Y)

    def isEqual(self, P):
        return self.X == P.getX() and self.Y == P.getY()

    