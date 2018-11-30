import numpy as np

def hamming(p, q):
    if(len(p) != len(q)): raise RuntimeError('length of two permutations not equals.')
    return len(p) - np.count_nonzero(p == q)

# Hamming distance
# def hamming(p, q):
#     if(len(p) != len(q)): raise RuntimeError('length of two permutations not equals.')

#     d = 0
#     for i in range(len(p)):
#         if(p[i] != q[i]):
#             d += 1

#     return d