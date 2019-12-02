import numpy as np  #type:ignore
from typing import Any, Callable, List, Dict, Tuple

def get_func(name:str, *, pathdata, angle_weight:float=None):

    name = name.lower()
    
    if name == 'aster':
        return pathdata.distance

    vecs = pathdata.nodes + [pathdata.home_poses[0]]
    origin = np.array(pathdata.home_poses[0])

    if name == 'angle':
        return get_precalced_func(lambda v1, v2: angle_distance(v1, v2, origin), vecs)
    
    if name == 'euclid':
        return get_precalced_func(euclid, vecs)

    if name == 'polar':
        return get_precalced_func(lambda v1, v2: polar_distance(v1, v2, origin), vecs)

    # if name == 'polar':
    #     if angle_weight is None: raise RuntimeError ('weight of angle not specified.')
    #     return get_precaled_polar_func(vecs, origin, angle_weight)
        

    raise RuntimeError('Unknown distance function')

    

def get_precalced_func(dist_func:Callable, vecs:List[Tuple]) -> Callable:
    return get_precalced_func_by_dists(get_precaled_dists(dist_func, vecs))


def get_precalced_func_by_dists(dists:Dict[Tuple[Any, Any], float]) -> Callable:
    return lambda v1, v2: dists[(v1, v2)]


def get_precaled_dists(dist_func:Callable, vecs:List[np.array]) -> Dict[Tuple[Any, Any], float]:
    return {(v1, v2):dist_func(np.array(v1), np.array(v2)) for v1 in vecs for v2 in vecs}


# def get_precaled_polar_func(vecs:List[Tuple], origin:np.array, angle_weight:float):
#     return get_precalced_func_by_dists(get_precaled_polar_dists(vecs, origin, angle_weight))


# def get_precaled_polar_dists(vecs:List[np.array], origin:np.array, angle_weight:float) -> Dict[Tuple[Tuple], float]:
#     radius_dists = get_precaled_dists(angle_distance, vecs)
#     max_radius_dist = max(radius_dists.values())

#     return {vec_pair: angle_weight * (angle_dist / 2) + (1 - angle_weight) * (radius_dists[vec_pair] / max_radius_dist)
#             for vec_pair, angle_dist in get_precaled_dists(angle_distance, vecs).items()}


def polar_distance(v1:np.array, v2:np.array, origin:np.array):
    ov1 = v1 - origin
    ov2 = v2 - origin
    cossim_val = cos_sim(ov1, ov2)
    if cossim_val is None: return None
    return np.pi/2 * abs(euclid_2s(ov1) - euclid_2s(ov2)) * np.arccos(cossim_val)


def radius_distance(v1:np.array, v2:np.array, origin:np.array):
    return abs(euclid(v1, origin) - euclid(v2, origin))


def angle_distance(v1:np.array, v2:np.array, origin:np.array):
    cos_sim_val = cos_sim(v1 - origin, v2 - origin)
    if cos_sim_val is None: return None
    return 1.0 - cos_sim_val


def cos_sim(v1:np.array, v2:np.array):
    norm_mul = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norm_mul == 0: return None
    return max(-1, min(np.dot(v1, v2) / norm_mul, 1))


def euclid(v1:np.array, v2:np.array):
    return np.linalg.norm(v2 - v1)


def euclid_2s(v:np.array):
    return np.inner(v, v)
