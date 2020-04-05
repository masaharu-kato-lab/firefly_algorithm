from typing import Optional, Iterable

# euclid distance
def euclid(vec1:Iterable, vec2:Optional[Iterable]=None) -> float:
    return euclid_sq(vec1, vec2) ** 0.5

# squared value of euclid distance
def euclid_sq(vec1:Iterable, vec2:Optional[Iterable]=None) -> float:
    if vec2 is None: return sum(elm ** 2 for elm in vec1)
    return euclid_sq(diff(vec1, vec2))

# difference of vectors
def diff(vec1:Iterable, vec2:Iterable) -> Iterable:
    return (elm2 - elm1 for elm1, elm2 in zip(vec1, vec2))

# consine similality
def cos_sim(vec1:Iterable, vec2:Iterable) -> float:
    norm_mul = euclid(vec1) * euclid(vec2)
    if norm_mul == 0: return None
    return max(-1, min(dot_prod(vec1, vec2) / norm_mul, 1))

# dot product
def dot_prod(vec1:Iterable, vec2:Iterable) -> Iterable:
    return (elm1 * elm2 for elm1, elm2 in zip(vec1, vec2))
