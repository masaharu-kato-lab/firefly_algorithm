#!env/bin/python
from collections import defaultdict
import argparse
import pickle
import sys
import os
from itertools import chain
import statistics

from attrdict import AttrDict #type:ignore

from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('input', nargs='+', type=str, help='Input binary pickle file path')
    argp.add_argument('-vmin', '--value_min'     , type=int, required=True, help='Minimum value')
    argp.add_argument('-vmax', '--value_max'     , type=int, required=True, help='Maximum value')
    argp.add_argument('-vinv', '--value_interval', type=int, required=True, help='Value interval')
    args = argp.parse_args()

    value_list = list(reversed(range(args.value_min, args.value_max + 1, args.value_interval)))
    print('\t'.join(['{:20}'.format(''), *('{:>10}'.format(x) for x in chain.from_iterable([x, '', '', '', ''] for x in value_list))]))
    print('\t'.join(['{:20}'.format(''), *('{:>10}'.format(x) for x in ['nf', 'min', 'max', 'mean', 'sd'] * len(value_list))]))
    
    nonetext = '{:>10}'.format('None')

    for _input in args.input:
        with open(_input, mode='rb') as f:
            binary = pickle.load(f)
            states_list = binary.states_by_seed.values()

        name = os.path.splitext(os.path.basename(_input))[0]
        times_of_states = [states_to_updates_until_value(states, value_list) for states in states_list]

        numvals_list = filter_numeric(times_of_states, value_list)

        print('\t'.join([
            '{:20}'.format(name),
            *chain.from_iterable(
                [
                    '{:10}'.format(nf),
                    '{:10.02f}'.format(vmin) if vmin is not None else nonetext,
                    '{:10.02f}'.format(vmax) if vmax is not None else nonetext,
                    '{:10.02f}'.format(ave)  if ave  is not None else nonetext,
                    '{:10.02f}'.format(sd)   if sd   is not None else nonetext,
                ]
                for nf, vmin, vmax, ave, sd in zip(
                    n_found       (numvals_list),
                    min_values    (numvals_list),
                    max_values    (numvals_list),
                    average_values(numvals_list),
                    sd_values     (numvals_list),
                )
            )
        ]))


def states_to_updates_until_value(_states:Dict[int, AttrDict], values:List[float]) -> Dict[float, int]:
    ret = {}
    states = iter(_states.values())
    c_state = next(states)
    for target_value in values:
        if c_state is not None:
            try:
                while c_state.best_plan.value > target_value:
                    c_state = next(states)
            except StopIteration:
                c_state = None

        if c_state is not None:
            ret[target_value] = c_state.n_updates
        else:
            ret[target_value] = None

    return ret



def average_values(numvals_list:List[float]) -> List[float]:
    return [statistics.mean(vals) if len(vals) else None for vals in numvals_list]

def sd_values(numvals_list:List[float]) -> List[Optional[float]]:
    return [statistics.stdev(vals) if len(vals) >= 2 else None for vals in numvals_list]

def n_found(numvals_list:List[float]) -> List[int]:
    return [len(vals) for vals in numvals_list]

def max_values(numvals_list:List[float]) -> List[Optional[float]]:
    return [max(vals) if len(vals) else None for vals in numvals_list]

def min_values(numvals_list:List[float]) -> List[Optional[float]]:
    return [min(vals) if len(vals) else None for vals in numvals_list]


def filter_numeric(values_list:List[List[Optional[float]]], xlist:Iterable[int]) -> List[float]:
    return [[values[x] for values in values_list if values[x] is not None] for x in xlist]


if __name__ == '__main__':
    main()
