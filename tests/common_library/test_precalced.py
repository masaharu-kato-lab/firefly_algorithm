import itertools
import pytest #type:ignore
import numpy as np #type:ignore
from common_library import precalced

params = [
    'func, args_list, ret',[
    [
        lambda v: 2 * v + 3,
        [(i,) for i in range(100)],
        {(i,) : 2 * i + 3 for i in range(100)},
    ], [
        lambda x, y: x * y,
        [(i, j) for j in range(20) for i in range(30)],
        {(i, j) : i * j for j in range(20) for i in range(30)},
    ]]
]

@pytest.mark.parametrize(*params)
def test_generate_vdict(func, args_list, ret):
    assert precalced.generate_vdict(func, args_list) == ret


@pytest.mark.parametrize(*params)
def test_precalced(func, args_list, ret):
    f = precalced.precalced(func, args_list)
    assert {args : f(*args) for args in args_list} == ret



def euclid_distance(p1, p2):
    return np.linalg.norm(np.array(p2) - np.array(p1))

def test_precalced_distance():
    points = [(45, 52), (192, 38), (114, 82), (241, 75), (123, 181)]
    dist = precalced.precalced_distance(euclid_distance, points)
    
    for pts in itertools.permutations(points, 2):
        assert dist(pts[0], pts[1]) == euclid_distance(pts[0], pts[1])
