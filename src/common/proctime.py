import time
from functools import wraps
from typing import Callable

def proctime(*funcs:Callable, n:int=1):
    times = []
    for func in funcs:
        start = time.time()
        _ = func() if n == 1 else [func() for _ in range(n)]
        end = time.time()
        times.append(end - start)
    return tuple(times)
