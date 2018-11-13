import math

def calc(coords : dict, perm : list, distance : callable):
    sum_distance = 0
    for i in range(len(perm)-1):
        sum_distance += distance(coords[perm[i]], coords[perm[i+1]])
    
    return sum_distance

def nint(x):
    return int(x + 0.5)

def euclid(coord1, coord2):
    diff = coord1 - coord2
    return nint(math.sqrt(sum(diff**2)))
    
def manhattan(coord1, coord2):
    return nint(sum(abs(coord1 - coord2)))

def maximum(coord1, coord2):
    return max(map(nint, abs(coord1 - coord2)))

def geographical(coord1, coord2):
    pass

def pseudo_euclidean(coord1, coord2):
    pass
