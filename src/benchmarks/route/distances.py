import math
from src.common.basic_math import  cos_sim, diff, euclid, euclid_sq
from typing import Any, Callable, Iterable, Optional

# distance based on polar coordinate
def polar_distance(v1:Iterable, v2:Iterable, origin:Iterable) -> Optional[float]:
    ov1 = diff(v1, origin)
    ov2 = diff(v2, origin)
    cossim_val = cos_sim(ov1, ov2)
    if cossim_val is None: return None
    return math.pi/2 * abs(diff(euclid_sq(ov1), euclid_sq(ov2))) * math.acos(cossim_val)


# distance based on radius
def radius_distance(v1:Iterable, v2:Iterable, origin:Iterable) -> float:
    return abs(diff(euclid(v1, origin), euclid(v2, origin)))


# distance based on angle
def angle_distance(v1:Iterable, v2:Iterable, origin:Iterable) -> Optional[float]:
    cos_sim_val = cos_sim(diff(v1, origin), diff(v2, origin))
    if cos_sim_val is None: return None
    return 1.0 - cos_sim_val
