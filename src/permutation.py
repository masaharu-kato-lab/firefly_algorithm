# Hamming distance
def distance(p, q):
    check_same_length(p, q)

    d = 0
    for i in range(len(p)):
        if(p[i] != q[i]):
            d += 1

    return d


def intersection(p, q):
    check_same_length(p, q)

    r = [None] * len(p)
    for i in range(len(p)):
        if(p[i] == q[i]):
            r[i] = p[i]
        pass
    
    return r




def check_same_length(p, q):
    if(len(p) != len(q)):
        raise RuntimeError('length of two permutations not equals.')

