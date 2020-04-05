import pytest
from common import nd_equation

@pytest.mark.parametrize(
    'coefs, prec, ret', [
        ([2, 1], 0.1, -2),
        ([3, 1], 0.01, -3),
        ([-100, 1], 0.05, 100),
        ([1, 4], 0.02, -0.25),
        # ([-1, 1, 1], 0.001, (5**0.5)/2 - 1/2),
    ]
)
def test_solve(coefs, prec, ret):
    assert nd_equation.solve(coefs, prec=prec) == ret


@pytest.mark.parametrize(
    'coefs, var, ret', [
        ([1], 10, 1),
        ([-25], 20, -25),
        ([17, -2, 3, 4], 0, 17),
        ([17, -2, 3, 4], 1, 22),
        ([17, -2, 3, 4], 3, 146),
        ([-3, -2, 1, -7, 5], 2, 21),
    ]
)
def test_assign(coefs, var, ret):
    assert nd_equation.assign(coefs, var) == ret
