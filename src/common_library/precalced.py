from typing import Any, Callable, List, Dict, Tuple, Iterable
import itertools

def precalced(func:Callable, args_list:Iterable[Iterable[Any]]) -> Callable:
    return lambda *args: precalced_with_vdict(generate_vdict(func, args_list))

def precalced_kw(func:Callable, kwargs_list:Iterable[Dict[str, Any]]) -> Callable:
    return lambda **kwargs: precalced_with_kwvdict(generate_kwvdict(func, kwargs_list))

def precalced_distance(dist_func:Callable, vecs:List[Any]) -> Callable:
    return lambda *args: precalced_with_vdict(generate_distance_vdict(dist_func, vecs))


def precalced_with_vdict(vdict:Dict[Iterable[Any], Any]) -> Callable:
    return lambda *args: vdict[args]

def precalced_with_kwvdict(kwvdict:Dict[Tuple[Tuple[str, Any]], Any]) -> Callable:
    return lambda **kwargs: kwvdict[tuple(kwargs.items())]


def generate_vdict(func:Callable, args_list:Iterable[Iterable[Any]]) -> Dict[Iterable[Any], Any]:
    return {args: func(*args) for args in args_list}

def generate_kwvdict(func:Callable, kwargs_list:Iterable[Dict[str, Any]]) -> Dict[Tuple[Tuple[str, Any]], Any]:
    return {tuple(kwargs.items()): func(*kwargs) for kwargs in kwargs_list}

def generate_distance_vdict(dist_func:Callable, vecs:List[Any]) -> Dict[Tuple[Any, Any], Any]:
    return generate_vdict(dist_func, itertools.permutations(vecs, r=2))

