from typing import Iterable

def hamming(p1:Iterable, p2:Iterable) -> int:
    return sum(c1 != c2 for c1, c2 in zip(p1, p2)) if len(p1) == len(p2) else None
