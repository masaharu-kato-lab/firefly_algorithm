import pytest #type:ignore
from common_library.multi_value import MultiValue

vcases = [
    ((10, 20), (15, 25)),
    ((18, 20), (15, 25)),
    ((15, 20), (15, 25)),
    ((15, 30), (15, 25)),
    ((15, 25), (15, 25)),
]

@pytest.mark.parametrize('v1, v2, ret', [(*v, r) for v, r in zip(vcases, [False, False, False, False, True])])
def test_eq(v1, v2, ret):
    assert (MultiValue(*v1) == MultiValue(*v2)) == ret
    
@pytest.mark.parametrize('v1, v2, ret', [(*v, r) for v, r in zip(vcases, [True, True, True, True, False])])
def test_ne(v1, v2, ret):
    assert (MultiValue(*v1) != MultiValue(*v2)) == ret
    
@pytest.mark.parametrize('v1, v2, ret', [(*v, r) for v, r in zip(vcases, [True, False, True, False, False])])
def test_lt(v1, v2, ret):
    assert (MultiValue(*v1) < MultiValue(*v2)) == ret
    
@pytest.mark.parametrize('v1, v2, ret', [(*v, r) for v, r in zip(vcases, [True, False, True, False, True])])
def test_le(v1, v2, ret):
    assert (MultiValue(*v1) <= MultiValue(*v2)) == ret
    
@pytest.mark.parametrize('v1, v2, ret', [(*v, r) for v, r in zip(vcases, [False, True, False, True, False])])
def test_gt(v1, v2, ret):
    assert (MultiValue(*v1) > MultiValue(*v2)) == ret
    
@pytest.mark.parametrize('v1, v2, ret', [(*v, r) for v, r in zip(vcases, [False, True, False, True, True])])
def test_ge(v1, v2, ret):
    assert (MultiValue(*v1) >= MultiValue(*v2)) == ret
    