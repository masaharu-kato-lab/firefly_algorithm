import numpy as np


def get_func(name:str, *, path_data, w_angle=None):
    
    if name == "aster":
        return path_data.distance

    vecs = path_data.nodes + [path_data.home_poses[0]]

    if name == "angle":
        return get_precalced_func(lambda v1, v2: angle_distance(v1, v2, path_data.home_poses[0]), vecs)
    
    if name == "euclid":
        return get_precalced_func(euclid, vecs)

    

def get_precalced_func(dist_func:callable, vecs:list) -> callable:
    dists = {(v1, v2):dist_func(v1, v2) for v1 in vecs for v2 in vecs}
    return lambda v1, v2: dists[(v1, v2)]


def angle_radius_distance(v1, v2, origin, w_angle:float):
    if v1 == v2: return 0
    _o = np.array(origin)
    return w_angle * angle_distance(v1, v2, origin) + (1.0 - w_angle) * abs(euclid(v1, _o) - euclid(v2, _o))


def angle_distance(v1, v2, origin):
    if v1 == v2: return 0
    _o = np.array(origin)
    cos_sim_val = cos_sim(np.array(v1) - _o, np.array(v2) - _o)
    if cos_sim_val is None: return None
    return 1.0 - cos_sim_val


def cos_sim(v1, v2):
    norm_mul = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norm_mul == 0: return None
    x = np.dot(v1, v2) / norm_mul
    return x


def euclid(v1, v2):
    return np.linalg.norm(v2 - v1)

