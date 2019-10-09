import numpy as np

def angle_distance(v1, v2, origin):
    if v1 == v2: return 0
    _o = np.array(origin)
    return 1.0 - cos_sim(np.array(v1) - _o, np.array(v2) - _o)


def cos_sim(v1, v2):
    x = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return x


def euclid(v1, v2):
    return np.linalg.norm(v2 - v1)
