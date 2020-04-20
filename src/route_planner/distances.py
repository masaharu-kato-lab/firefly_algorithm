import numpy as np  #type:ignore
from typing import Any, Callable, List, Dict, Tuple, Iterable


def compare_multiple(d1:Tuple, d2:Tuple) -> int:
    for v1, v2 in zip(d1, d2):
        diff = v1 - v2
        if diff > 0: return 1
        if diff < 0: return -1
    return 0


def get_multiple_func(names:Iterable[str], *, pathdata) -> Callable:

    vecs = pathdata.nodes + [pathdata.home_poses[0]]
    return get_precalced_func(
        lambda v1, v2: tuple(_get_raw_func(name, pathdata=pathdata)(v1, v2) for name in names),
        vecs
    )


def get_func(name:str, *, pathdata) -> Callable:

    vecs = pathdata.nodes + [pathdata.home_poses[0]]
    return get_precalced_func(_get_raw_func(name, pathdata=pathdata), vecs)


def _get_raw_func(name:str, *, pathdata) -> Callable:
    
    name = name.lower()
    
    if name == 'aster':
        return pathdata.distance

    origin = np.array(pathdata.home_poses[0])

    if name == 'angle':
        return lambda v1, v2: angle_distance(v1, v2, origin)
    
    if name == 'euclid':
        return euclid

    if name == 'polar':
        return lambda v1, v2: polar_distance(v1, v2, origin)


    raise RuntimeError('Unknown distance function')

    

def get_precalced_func(dist_func:Callable, vecs:List[Tuple]) -> Callable:
    d = _get_precaled_dist_dict(dist_func, vecs)
    return _get_precalced_func_by_dists(d)


def _get_precalced_func_by_dists(dists:Dict[Tuple[Any, Any], float]) -> Callable:
    return lambda v1, v2: dists[(v1, v2)]


def _get_precaled_dist_dict(dist_func:Callable, vecs:list) -> Dict[Tuple[Any, Any], float]:
    return {(v1, v2):dist_func(v1, v2) for v1 in vecs for v2 in vecs}


# def get_precaled_polar_func(vecs:List[Tuple], origin:np.array, angle_weight:float):
#     return get_precalced_func_by_dists(get_precaled_polar_dists(vecs, origin, angle_weight))


# def get_precaled_polar_dists(vecs:List[np.array], origin:np.array, angle_weight:float) -> Dict[Tuple[Tuple], float]:
#     radius_dists = get_precaled_dists(angle_distance, vecs)
#     max_radius_dist = max(radius_dists.values())

#     return {vec_pair: angle_weight * (angle_dist / 2) + (1 - angle_weight) * (radius_dists[vec_pair] / max_radius_dist)
#             for vec_pair, angle_dist in get_precaled_dists(angle_distance, vecs).items()}


def polar_distance(v1, v2, origin):
    ov1 = np.array(v1) - np.array(origin)
    ov2 = np.array(v2) - np.array(origin)
    cossim_val = cos_sim(ov1, ov2)
    if cossim_val is None: return None
    return np.pi/2 * abs(euclid_2s(ov1) - euclid_2s(ov2)) * np.arccos(cossim_val)


def radius_distance(v1, v2, origin):
    return abs(euclid(v1, origin) - euclid(v2, origin))


def angle_distance(v1, v2, origin):
    cos_sim_val = cos_sim(np.array(v1) - np.array(origin), np.array(v2) - np.array(origin))
    if cos_sim_val is None: return None
    return 1.0 - cos_sim_val


def cos_sim(v1, v2):
    norm_mul = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norm_mul == 0: return None
    return max(-1, min(np.dot(v1, v2) / norm_mul, 1))


def euclid(v1, v2):
    return np.linalg.norm(np.array(v2) - np.array(v1))


def euclid_2s(v):
    return np.inner(v, v)
