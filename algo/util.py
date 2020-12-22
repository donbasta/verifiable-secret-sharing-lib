from math import gcd
from primelibpy import Prime as p
import random

def pollard_rho(n):
    x = 2
    y = 2
    d = 1
    f = lambda x: (x ** 2 + 1) % n
    while d == 1:
        x = f(x)
        y = f(f(y))
        d = gcd(abs(x - y), n)
    if d != n:
        return d

def test():
    return p.getSophieGermainPrime(1, 100)

def semi_primitive_root(p):
    phi = (p - 1) // 2
    n = phi
    i = 2
    fact = []
    while i * i <= n:
        if n % i == 0:
            fact.append(i)
            while n % i == 0:
                n = n // i
        i += 1
    if n > 1:
        fact.append(n)
    lul = []
    for res in range(2, p):
        ok = True
        ok &= (pow(res, phi, p) == 1)
        for prfact in fact:
            ok &= (pow(res, phi // prfact, p) != 1)
        if ok:
            # print("res", res)
            lul.append(res)
        if len(lul) >= 2:
            break
    sz = len(lul)
    if sz == 0:
        return -1
    else:
        return lul[random.randint(0, sz - 1)]

def primitive_root(p):
    phi = p - 1
    n = phi
    i = 2
    fact = []
    while i * i <= n:
        if n % i == 0:
            fact.append(i)
            while n % i == 0:
                n = n // i
        i += 1
    if n > 1:
        fact.append(n)
    
    for res in range(2, p):
        ok = True
        for prfact in fact:
            ok &= pow(res, phi // prfact, p) != 1
        if ok:
            return res
    return -1

if __name__ == "__main__":
    # n = 37577342607448995717608254102946226377108444520819892279347966
    # p = pollard_rho(n)
    # assert n % p == 0
    # print ("{} = {} * {}".format(n, p, n/p))
    for i in [3,5,7,11,13,17,23]:
        print(primitive_root(i))