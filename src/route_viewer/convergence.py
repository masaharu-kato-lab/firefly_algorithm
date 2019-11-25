#!env/bin/python
from collections import defaultdict
import argparse
import os
import pickle
import sys

from attrdict import AttrDict #type:ignore
import matplotlib.pyplot as plt #type:ignore

from typing import Any, Callable, Dict, Iterable, Iterator, List
State = AttrDict
States = Dict[int, State]

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument(            'input' , type=str, help='Input binary pickle file path')
    argp.add_argument('-o'   , '--output' , type=str, default=None, help='Output figure file directory (None to display)')
    # argp.add_argument('-imin', '--itr_min', type=int, default = 0  , help='Minimum iteration')
    argp.add_argument('-xn', '--x_number', type=int, help='Maximum iteration')
    # argp.add_argument('-iinv', '--itr_inv', type=int, default = 5  , help='Interval of iteration')
    argp.add_argument('-x'   , '--xtype'  , type=str, choices=['iteration', 'update'], default='iteration', help='Value type for x-value of graph')
    argp.add_argument('-y'   , '--ytype'  , type=str, choices=['value'], default='value', help='Value type for y-value of graph')
    argp.add_argument('-sx'  , '--size_x' , type=float, default=12, help='Figure size x (inch)')
    argp.add_argument('-sy'  , '--size_y' , type=float, default=8, help='Figure size y (inch)')
    argp.add_argument('-dpi' , '--dpi'    , type=float, default=200, help='Figure DPI (pixel per inch)')
    argp.add_argument('-t'   , '--title'  , type=str, default=None, help='Title formatted text')
    args = argp.parse_args()

    get_itrs:Callable[[States], List[int]] = {
        'iteration': lambda states: states.keys(),
        'update'   : lambda states: (state.itr for state in states.values() if state.itr == state.best_itr)
    }[args.xtype]

    get_values:Callable[[State], float] = {
        'value': lambda state: state.best_plan.value,
    }[args.ytype]

    with open(args.input, mode='rb') as f:
        binary = pickle.load(f)
        states_list = binary.states_by_seed.values()

        itrs_list = [[*get_itrs(states)] for states in states_list]
        max_n_itrs = args.x_number or max(len(itrs) for itrs in itrs_list)
        itr_indexes = [*range(max_n_itrs)]
        full_itrs_list = [[*fixed(itrs, max_n_itrs)] for itrs in itrs_list]
        # data = [[get_values(states[itr]) for itr in itrs] for states, itrs in zip(states_list, full_itrs_list)]
        data = [[get_values(states[itrs[itr_index]]) for states, itrs in zip(states_list, full_itrs_list)] for itr_index in itr_indexes]

    plt.figure(figsize=(args.size_x, args.size_y))
    plt.boxplot(data)
    plt.xticks([*range(1, len(itr_indexes)+1)], itr_indexes)
    if args.title: plt.title(args.title)

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.show()

    plt.close()


def make_data(args, states_list:List[List[AttrDict]]):

    itrs = list(range(args.itr_min, args.itr_max+1, args.itr_inv))

    values_on_itrs = defaultdict(lambda: []) 

    for states in states_list:
        for itr in itrs:
            state = states[itr]
            values_on_itrs[state.itr].append(state.best_plan.value)


def fixed(iterable:Iterable[Any], n:int) -> Iterator[Any]:
    for value in iterable:
        yield value
        n -= 1
        if not n: return
    if n > 0:
        for _ in range(n):
            yield value



if __name__ == '__main__':
    main()
