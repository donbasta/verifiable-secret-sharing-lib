class Commit:
    def __init__(commits, g, p):
        self.generator = g
        self.prime = p
        self.commits = commit

def distribute_commit(dealer):
    p = dealer.prime
    q = (p - 1) // 2 #safe prime of the sophie germain prime p
    g = primitive_root(q)
    koefs = dealer.polynomial.coefficients
    commits = [pow(g, koef, q) for koef in koefs]
    return Commit(commits, g, q)

def validate(commit, holder):
    point = holder.point
    share = holder.share
    commits = commit.commits
    p = commit.p
    g = commit.g
    cek1 = 1
    for i in range(len(commits)):
        cek1 = (cek1 * pow(commits[i], pow(point, i, p - 1), p)) % p
    cek2 = pow(g, share, p)
    return cek1 == cek2


