#!env/bin/python
from collections import defaultdict
import argparse
import os
import pickle
import sys

import matplotlib.pyplot as plt #type:ignore

from typing import Any, Callable, Dict, Iterable, Iterator, List
State = AttrDict
States = Dict[int, State]

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument(            'inputs'   , type=str, nargs='+', help='Input binary pickle file path')
    argp.add_argument('-o'   , '--output'    , type=str, default=None, help='Output figure file directory (None to display)')
    # argp.add_argument('-xmin', '--x_min'     , type=int, default=0, help='Minimum X value')
    argp.add_argument('-xmax', '--x_max'     , type=int, required=True, help='Maximum X value')
    argp.add_argument('-xinv', '--x_interval', type=int, default=1, help='X value interval')
    argp.add_argument('-sx'  , '--size_x'    , type=float, default=12, help='Figure size x (inch)')
    argp.add_argument('-sy'  , '--size_y'    , type=float, default=8, help='Figure size y (inch)')
    argp.add_argument('-dpi' , '--dpi'       , type=float, default=200, help='Figure DPI (pixel per inch)')
    argp.add_argument('-t'   , '--title'     , type=str, default=None, help='Title formatted text')
    args = argp.parse_args()

    colormap = plt.get_cmap("tab10")

    plt.figure(figsize=(args.size_x, args.size_y))

    for i, _input in enumerate(args.inputs):
        with open(_input, mode='rb') as f:
            binary = pickle.load(f)
            states_list = binary.states_by_seed.values()

        xlist = range(0, args.x_max, args.x_interval)
        values = [[*states_to_values_by_update(states)] for states in states_list]

        plt.plot(xlist, average_values(values, xlist), color=colormap(i),
            label=os.path.splitext(os.path.basename(_input))[0]
        )
        plt.plot(xlist, min_values(values, xlist), color=colormap(i), linestyle='dotted')
        plt.plot(xlist, max_values(values, xlist), color=colormap(i), linestyle='dotted')


    plt.legend()
    plt.xlabel('updates')
    plt.ylabel("best firefly's luminosity")

    if args.title: plt.title(args.title)

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.show()

    plt.close()


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
