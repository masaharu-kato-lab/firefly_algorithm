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
    argp.add_argument('-o'   , '--output'    , type=str, required=True, help='Output path statistics file')
    argp.add_argument('-xmax', '--x_max'     , type=int, required=True, help='Maximum X value')
    argp.add_argument('-xinv', '--x_interval', type=int, default=1, help='X value interval')
    args = argp.parse_args()

    xlist = range(0, args.x_max+1, args.x_interval)
    
    for i, _input in enumerate(args.inputs):
        with open(_input, mode='rb') as f:
            binary = pickle.load(f)
            states_list = binary.states_by_seed.values()

        with open(args.output, mode='w') as f:
            print('\t'.join('{:11}'.format(x) for x in xlist), file=f)
            for states in states_list:
                values = [*states_to_values_by_update(states)]
                print('\t'.join('{:11.3f}'.format(v) for v in (get_value_from_values(values, x) for x in xlist)), file=f)



def states_to_values_by_update(states) -> Iterator[float]:
    for state in states.values():
        value = state.best_plan.value
        for _ in range(state.current_n_updates):
            yield value


def get_values(values_list:List[List[float]], xlist:Iterable[int]) -> List[List[float]]:
    return [[get_value_from_values(values, x) for values in values_list] for x in xlist]


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
