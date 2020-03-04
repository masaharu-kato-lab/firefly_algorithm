import numpy as np #type:ignore

# euclid distance
def euclid(v1, v2) -> float:
    return np.linalg.norm(np.array(v2) - np.array(v1))

# squared value of euclid distance
def euclid_2s(_v) -> float:
    v = np.array(_v)
    return np.inner(v, v)

# consine similality
def cos_sim(_v1, _v2) -> float:
    v1 = np.array(_v1)
    v2 = np.array(_v2)
    norm_mul = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norm_mul == 0: return None
    return max(-1, min(np.dot(v1, v2) / norm_mul, 1))
