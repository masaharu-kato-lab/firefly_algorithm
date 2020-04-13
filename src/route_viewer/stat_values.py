#!env/bin/python
from collections import defaultdict
import argparse
import pickle
import sys
import os
from itertools import chain
import statistics

from attrdict import AttrDict #type:ignore

from typing import Any, Callable, Dict, Iterable, Iterator, List

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('input', nargs='+', type=str, help='Input binary pickle file path')
    argp.add_argument('-xmax', '--x_max'     , type=int, required=True, help='Maximum X value')
    argp.add_argument('-xinv', '--x_interval', type=int, required=True, help='X value interval')
    argp.add_argument('-t'   , '--stat_types', nargs='+', type=str, default=['mean'], choices=['min', 'max', 'mean', 'sd'], help='Statistic value types')
    args = argp.parse_args()

    xlist = range(0, args.x_max+1, args.x_interval)
    
    # print x value (number of updates)
    print('\t'.join(['{:20}'.format(''), *('{:>10}'.format(x) for x in chain.from_iterable(
        [x, *([''] * (len(args.stat_types) - 1))] for x in xlist))]
    ))
    
    # print statistics type if multiple statistics types are specified
    if len(args.stat_types) > 1:
        print('\t'.join(['{:20}'.format(''), *('{:>10}'.format(x) for x in args.stat_types * len(xlist))]))
    
    calcer_dict = {
        'min' : lambda values, xlist: min_values(values, xlist),
        'max' : lambda values, xlist: max_values(values, xlist),
        'mean': lambda values, xlist: average_values(values, xlist),
        'sd'  : lambda values, xlist: sd_values(values, xlist),
    }

    calcers = [calcer_dict[stat_type] for stat_type in args.stat_types]

    for _input in args.input:
        with open(_input, mode='rb') as f:
            binary = pickle.load(f)
            states_list = binary.states_by_seed.values()

        name = os.path.splitext(os.path.basename(_input))[0]
        values = [[*states_to_values_by_update(states)] for states in states_list]

        stat_values = (calcer(values, xlist) for calcer in calcers)

        print('\t'.join([
            '{:20}'.format(name),
            *chain.from_iterable(('{:10.03f}'.format(value) for value in value_tuple) for value_tuple in zip(*stat_values))
        ]))



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


def sd_values(values_list:List[List[float]], xlist:Iterable[int]) -> List[float]:
    return [statistics.stdev(get_value_from_values(values, x) for values in values_list) for x in xlist]


def min_values(values_list:List[List[float]], xlist:Iterable[int]) -> List[float]:
    return [min(get_value_from_values(values, x) for values in values_list) for x in xlist]


def max_values(values_list:List[List[float]], xlist:Iterable[int]) -> List[float]:
    return [max(get_value_from_values(values, x) for values in values_list) for x in xlist]

if __name__ == '__main__':
    main()
