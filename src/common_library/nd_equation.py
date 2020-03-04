import math
from typing import List, Callable

def calc(coefs:List[float], x:float) -> float:
    current = 0.0
    for coef in reversed(coefs):
        current = current * x + coef
    return current


def get_calcer(coefs:List[float]) -> Callable:
    return lambda x: calc(coefs, x)


def get_derivative_coefs(coefs:List[float]) -> List[float]:
    return [i * coef for i, coef in enumerate(coefs[1:], 1)]


def get_derivative_calcer(coefs:List[float]) -> Callable:
    d_coefs = get_derivative_coefs(coefs)
    return lambda x: calc(d_coefs, x)


def solve_with_newton(*, f:Callable, df:Callable, prec:float, init:float = 0):
    x = init
    c = 0
    while True:
        x_new = x - f(x) / df(x)
        if abs(x_new - x) < prec : break
        x = x_new
        c += 1
    return x


def solve(coefs:list, *, prec:float, init:float = 0):
    return solve_with_newton(
        f = get_calcer(coefs),
        df = get_derivative_calcer(coefs),
        prec = prec,
        init = init
    )

