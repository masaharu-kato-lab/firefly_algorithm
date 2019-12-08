#!env/bin/python
from collections import defaultdict
import argparse
import pickle
import sys
import os

from attrdict import AttrDict #type:ignore

from typing import Any, Callable, Dict, Iterable, Iterator, List
State = AttrDict
States = Dict[int, State]

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('inputs', type=str, nargs='+', help='Input binary pickle file path')
    argp.add_argument('-x', '--x', type=int, nargs='+', required=True, help='X value (number of updates)')
    args = argp.parse_args()

    for i, _input in enumerate(args.inputs):
        with open(_input, mode='rb') as f:
            binary = pickle.load(f)
            states_list = binary.states_by_seed.values()

        values = [[*states_to_values_by_update(states)] for states in states_list]
        yvals = 




def states_to_values_by_update(states) -> Iterator[float]:
    for state in states.values():
        value = state.best_plan.value
        for _ in range(state.current_n_updates):
            yield value


def average_values(values_list:List[List[float]], xlist:Iterable[int]) -> List[float]:
    n = len(values_list)
    return [sum(get_value_from_values(values, x) for values in values_list) / n for x in xlist]


def max_values(values_list:List[List[float]], xlist:Iterable[int]) -> List[float]:
    return [max(get_value_from_values(values, x) for values in values_list) for x in xlist]


def min_values(values_list:List[List[float]], xlist:Iterable[int]) -> List[float]:
    return [min(get_value_from_values(values, x) for values in values_list) for x in xlist]


def get_value_from_values(values:List[float], index:int) -> float:
    if index >= len(values): return values[-1]
    return values[index]


if __name__ == '__main__':
    main()
