#!env/bin/python
from collections import defaultdict
import argparse
import pickle
import sys
import os

from attrdict import AttrDict #type:ignore

from typing import Any, Callable, Dict, Iterable, Iterator, List

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('input', nargs='+', type=str, help='Input binary pickle file path')
    argp.add_argument('-xmax', '--x_max'     , type=int, required=True, help='Maximum X value')
    argp.add_argument('-xinv', '--x_interval', type=int, default=1, help='X value interval')
    args = argp.parse_args()

    xlist = range(0, args.x_max+1, args.x_interval)
    print('\t'.join(['{:20}'.format(''), *('{:11}'.format(x) for x in xlist)]))
    
    for _input in args.input:
        with open(_input, mode='rb') as f:
            binary = pickle.load(f)
            states_list = binary.states_by_seed.values()

        name = os.path.splitext(os.path.basename(_input))[0]
        values = [[*states_to_values_by_update(states)] for states in states_list]

        print('\t'.join(['{:20}'.format(name), *('{:11.3f}'.format(v) for v in average_values(values, xlist))]))



def states_to_values_by_update(states:Dict[int, AttrDict]) -> Iterator[float]:
    for state in states.values():
        value = state.best_plan.value
        for _ in range(state.current_n_updates):
            yield value


def get_value_from_values(values:List[float], index:int) -> float:
    if index >= len(values): return values[-1]
    return values[index]


def average_values(values_list:List[List[float]], xlist:Iterable[int]) -> List[float]:
    n = len(values_list)
    return [sum(get_value_from_values(values, x) for values in values_list) / n for x in xlist]


if __name__ == '__main__':
    main()
