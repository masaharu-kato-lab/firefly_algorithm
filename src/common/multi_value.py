import functools
from typing import Any

# Dual distance consisting of aster and euclid
@functools.total_ordering
class MultiValue:
    def __init__(self, *values:Any):
        self.values = values

    
    def __eq__(self, other) -> bool:
        if not isinstance(other, MultiValue): return NotImplemented
        if len(self.values) != len(other.values): raise RuntimeError('Different length of values.')

        return all(self_v == other_v for self_v, other_v in zip(self.values, other.values))


    def __lt__(self, other) -> bool:
        if not isinstance(other, MultiValue): return NotImplemented
        if len(self.values) != len(other.values): raise RuntimeError('Different length of values.')

        for self_v, other_v in zip(self.values, other.values):
            if self_v != other_v:
                return self_v < other_v

        return False
