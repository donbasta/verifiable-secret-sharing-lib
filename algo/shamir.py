from Crypto.Util.number import getPrime
from primelibpy import Prime as pr
from const import SOPHIE_GERMAIN_PRIMES as sgp
from util import semi_primitive_root
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
    def __init__(self, point, share, prime, vss=None):
        #share is the y coordinate, point is the x coordinate
        #prime is the prime used for the field
        self.point = point
        self.share = share
        self.prime = prime
        self.vss = vss
    
    def __str__(self):
        return "x: {}, y: {}".format(self.point, self.share)

class ShamirDealer:
    def __init__(self, t, n, s=None, p=None, vss="Feldman"):
        self.secret = s
        self.numholders = n
        self.threshold = t
        if p == None:
            # dig = math.ceil(max(math.log2(n), math.log2(s)))
            # bit = random.randint(2 * dig + 1, 4 * dig)
            # if verif:
            #     print("tes: {} {}".format(2**bit, 2**(bit+1)))
            #     self.prime = pr.getSophieGermainPrime(2 ** bit, 2 ** (bit + 1))[0]
            #     self.qrime = 2 * self.prime + 1
            #generate big prime p here using lib,
            #greater than s and n
            # self.prime = getPrime(bit)
            # cur = (sgp[-1] * 2) + 1
            cur = sgp[-1]
            if cur < s or cur < n:
                raise Exception("Number of holder or the secret is too big")
            self.prime = cur
            pass
        else:
            self.prime = p
        self.vss = vss
        if vss == "Feldman":
            self.polynomial = self.generate_polynomial(c="secret")
        elif vss == "Pedersen":
            self.polynomial = (self.generate_polynomial(c="secret"), self.generate_polynomial())
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
    
    def generate_polynomial(self, c=None):
        if c == "secret":
            koef = [self.secret]
        else:
            koef = [random.randint(0, self.prime - 1)]
        for i in range(1, self.threshold):
            #generate random integers between 0 and p - 1 inclusive
            a = random.randint(0, self.prime - 1)
            koef.append(a)
        return Polynomial(koef, self.prime)
    
    def generate_share(self):
        shares = []
        if self.vss == "Feldman":
            for point in self.holders:
                share = self.polynomial.calc(point)
                shares.append((point, share, self.prime))
        elif self.vss == "Pedersen":
            for point in self.holders:
                share0 = self.polynomial[0].calc(point)
                share1 = self.polynomial[1].calc(point)
                shares.append((point, (share0, share1), self.prime))
        self.shares = shares
    
    def generate_commitments(self):
        p = self.prime
        q = 2 * p + 1
        g = semi_primitive_root(q)
        print("generator: {}, prime: {}".format(g, q))
        if self.vss == "Feldman":
            koefs = self.polynomial.coefficients
            commits = [pow(g, koef, q) for koef in koefs]
            h = None
            return Commit(commits, g, h, q, self.vss)
        elif self.vss == "Pedersen":
            koefs0 = self.polynomial[0].coefficients
            koefs1 = self.polynomial[1].coefficients
            print(koefs0, koefs1)
            # h = random.randint(2, q - 1)
            h = semi_primitive_root(q)
            while h == g:
                h = semi_primitive_root(q)
            print("g = {}, h = {}".format(g, h))
            # print(pow(g, koefs0[0], q) * pow(h, koefs1[0], q))
            commits = [(pow(g, koefs0[i], q) * pow(h, koefs1[i], q) % q) for i in range(len(koefs0))]
            # commits = [(pow(g, koefs0[i], q) * pow(h, koefs1[i], q) % q) for i in range()]
            return Commit(commits, g, h, q, self.vss)
    
    def distribute(self):
        self.generate_share()
        return [
            ShamirHolder(self.shares[i][0], self.shares[i][1], self.prime) for i in range(len(self.shares))
        ]

class Commit:
    def __init__(self, commits, g, h, p, vss="Feldman"):
        self.generator = g
        self.prime = p
        self.commits = commits
        self.vss = vss
        if vss == "Pedersen":
            self.other = h

def distribute_commit(dealer):
    p = dealer.prime
    # q = (p - 1) // 2 #safe prime of the sophie germain prime p
    q = 2 * p + 1
    # q = p
    # g = semi_primitive_root(p)
    g = semi_primitive_root(q)
    print("generator: {}, prime: {}".format(g, q))
    koefs = dealer.polynomial.coefficients
    commits = [pow(g, koef, q) for koef in koefs]
    h = None
    return Commit(commits, g, h, q)

def validate(commit, holder):
    point = holder.point
    share = holder.share
    commits = commit.commits
    vss = commit.vss
    p = commit.prime
    g = commit.generator
    if vss == "Feldman":
        cek1 = 1
        for i in range(len(commits)):
            cek1 = (cek1 * pow(commits[i], pow(point, i, p - 1), p)) % p
        cek2 = pow(g, share, p)
        print("{} {} {} {}".format(point, share, cek1, cek2))
        return cek1 == cek2
    elif vss == "Pedersen":
        cek1 = 1
        for i in range(len(commits)):
            cek1 = (cek1 * pow(commits[i], pow(point, i, p - 1), p)) % p
        h = commit.other
        cek2 = (pow(g, share[0], p) * pow(h, share[1], p)) % p
        return cek1 == cek2

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

if __name__ == "__main__":

    t = 5
    n = 10
    secret = 23456
    dealer = ShamirDealer(t, n, secret, None, "Pedersen")
    # print("Polynomial: {}".format(dealer.polynomial.coefficients))
    holders = dealer.distribute()
    print("prime: {}".format(dealer.prime))

    i = 0
    for holder in holders:
        i += 1
        print("The {}th holder holds following share: ".format(i), end='')
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
    
    # commit = distribute_commit(dealer)
    commit = dealer.generate_commitments()
    print("commits: {}".format([c for c in commit.commits]))
    for holder in holders:
        print(validate(commit, holder))



    
