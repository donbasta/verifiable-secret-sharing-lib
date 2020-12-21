from Crypto.Util.number import getPrime
import math
import random

class Polynomial:
    def __init__(self, c, p):
        self.coefficients = [co % p for co in c]
        self.mod = p
    
    def set_koef(self, n, a):
        while n >= len(self.coefficients):
            self.coefficients.append(0)
        self.coefficients[n] = a % self.mod
    
    def get_degree(self):
        return len(self.coefficients) - 1
    
    def calc(self, x):
        res = 0
        for i in range(len(self.coefficients) - 1, -1, -1):
            res = (res * x + self.coefficients[i]) % self.mod
        return res

class ShamirHolder:
    def __init__(self, point, share, prime):
        #share is the y coordinate, point is the x coordinate
        #prime is the prime used for the field
        self.point = point
        self.share = share
        self.prime = prime
    
    def __str__(self):
        return "x: {}, y: {}".format(self.point, self.share)

class ShamirDealer:
    def __init__(self, t, n, s=None, p=None):
        self.secret = s
        self.numholders = n
        self.threshold = t
        if p == None:
            dig = math.ceil(max(math.log2(n), math.log2(s)))
            bit = random.randint(dig + 1, 2 * dig)
            #generate big prime p here using lib,
            #greater than s and n
            self.prime = getPrime(bit)
            pass
        else:
            self.prime = p
        self.polynomial = self.generate_polynomial()
        self.holders = self.generate_x()
    
    def set_secret(self, s):
        if s > self.prime:
            raise "Secret is too long to be shared"
        self.secret = s
    
    def get_prime(self):
        return self.prime
    
    def generate_x(self):
        x_coordinates = []
        for i in range(self.numholders):
            #append random generated xi for each participants
            #all different
            a = random.randint(0, self.prime - 1)
            while a in x_coordinates:
                a = random.randint(0, self.prime - 1)
            x_coordinates.append(a)
        return x_coordinates
    
    def generate_polynomial(self):
        koef = [self.secret]
        for i in range(1, self.threshold):
            #generate random integers between 0 and p - 1 inclusive
            a = random.randint(0, self.prime - 1)
            koef.append(a)
        return Polynomial(koef, self.prime)
    
    def generate_share(self):
        shares = []
        for point in self.holders:
            share = self.polynomial.calc(point)
            shares.append((point, share, self.prime))
        self.shares = shares
    
    def generate_validate(self):
        pass
    
    def distribute(self):
        self.generate_share()
        return [
            ShamirHolder(self.shares[i][0], self.shares[i][1], self.prime) for i in range(len(self.shares))
        ]

def interpolate(points, mod, calc):
    res = 0
    for (x, y) in points:
        temp = y
        cnt = 0
        for (x1, y1) in points:
            if x1 == x:
                continue
            cnt += 1
            temp = (temp * (calc - x1) * pow(x - x1, -1, mod)) % mod
        assert cnt == len(points) - 1
        res = (res + temp) % mod
    return res

def reconstruction(holders, threshold):
    mod = holders[0].prime
    for holder in holders:
        if holder.prime != mod:
            raise
            raise Exception("Invalid shares, cannot reconstruct secret")
    if len(holders) < threshold:
        raise Exception("Not enough information to reconstruct secret")
    points = [(holder.point, holder.share) for holder in holders]
    return interpolate(points, mod, 0)
    
def validate():
    pass

if __name__ == "__main__":

    t = 8
    n = 10
    secret = 123456789101112131415
    dealer = ShamirDealer(t, n, secret)
    holders = dealer.distribute()

    i = 0
    for holder in holders:
        i += 1
        print("The {}th holder holds following share".format(i), end='')
        print(holder)

    try:
        rec = reconstruction(holders[:7], t)
        print(rec)
    except Exception as e:
        print(e)

    try:
        rec = reconstruction(holders[:8], t)
        print(rec)
    except Exception as e:
        print(e)
    
    try:
        rec = reconstruction(holders, t)
        print(rec)
    except Exception as e:
        print(e)
    
    try:
        rec = reconstruction(holders[1:], t)
        print(rec)
    except Exception as e:
        print(e)



    
