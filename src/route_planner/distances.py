from typing import Any, Callable, List, Dict, Tuple
import numpy as np  #type:ignore
from route_planner import drone_simulator
from common.precalced import precalced_distance
from common.basic_distance import euclid, euclid_2s, cos_sim
from common.multi_value import MultiValue

# get specified distance function
def get_function(name:str, *, pathdata:drone_simulator.PathData, angle_weight:float=None) -> Callable:

    # convert `name` to lower cases
    name = name.lower()
    
    if name == 'aster':
        return pathdata.distance

    vecs = pathdata.nodes + [pathdata.home_poses[0]]
    origin = np.array(pathdata.home_poses[0])
    
    if name == 'euclid':
        return precalced_distance(euclid, vecs)

    if name == 'aster_euclid':
        return precalced_distance(lambda v1, v2: MultiValue(pathdata.distance(v1, v2), euclid(v1, v2)), vecs)

    if name == 'angle':
        return precalced_distance(lambda v1, v2: angle_distance(v1, v2, origin), vecs)

    if name == 'polar':
        return precalced_distance(lambda v1, v2: polar_distance(v1, v2, origin), vecs)

    # if name == 'polar':
    #     if angle_weight is None: raise RuntimeError ('weight of angle not specified.')
    #     return get_precaled_polar_func(vecs, origin, angle_weight)
        
    raise RuntimeError('Unknown distance function')


# distance based on polar coordinate
def polar_distance(v1:np.array, v2:np.array, origin:np.array) -> float:
    ov1 = v1 - origin
    ov2 = v2 - origin
    cossim_val = cos_sim(ov1, ov2)
    if cossim_val is None: return None
    return np.pi/2 * abs(euclid_2s(ov1) - euclid_2s(ov2)) * np.arccos(cossim_val)

# distance based on radius
def radius_distance(v1:np.array, v2:np.array, origin:np.array) -> float:
    return abs(euclid(v1, origin) - euclid(v2, origin))

# distance based on angle
def angle_distance(v1:np.array, v2:np.array, origin:np.array) -> float:
    cos_sim_val = cos_sim(v1 - origin, v2 - origin)
    if cos_sim_val is None: return None
    return 1.0 - cos_sim_val

