#!env/bin/python
import argparse
from datetime import datetime
import numpy as np #type:ignore
import pickle
from attrdict import AttrDict #type:ignore

import _arguments
import distances
import firefly_with_log
import init
import log
import route

from typing import Callable, Dict

def main():

    try:
        args = _arguments.parse()
    except RuntimeError as e:
        print('Argument Error: {}'.format(e))
        return -1


    path_data = route.PathData(args.input)
    calc_value = get_calc_value(args, path_data=path_data)
    states_by_seed:Dict[int, Dict[int, AttrDict]] = {}

    for seed in range(args.seed, args.seed + args.n_run):

        args.seed = seed
        args.init_seed = (seed - args.seed) + args.init_seed
        args.output_filename = '{}/{}.txt'.format(args.output, datetime.now().strftime("%Y%m%d_%H%M%S_%f")) if args.n_run > 1 else '{}.txt'.format(args.output)

        states_by_seed[args.seed] = firefly_with_log.run(args, path_data = path_data, calc_value = calc_value)


    if not args.no_binary_output:
        out_bin = AttrDict()
        out_bin.args = args
        out_bin.states_by_seed = states_by_seed
        out_bin.final_states_by_seed = {seed:list(states.items())[-1][1] for seed, states in states_by_seed.items()}
        
        path = args.binary_output if args.binary_output is not None else args.output + '.pickle'
        log.prepare_directory(path)
        with open(path, mode='wb') as f:
            pickle.dump(out_bin, file = f)


def get_calc_value(args, *, path_data:route.PathData) -> Callable:

    plan_generator = route.PlanGenerator(
        path_data = path_data,
        drone_prop = route.DroneProperty(path_data),
        n_drones = args.n_drones,
        safety_weight = args.safety_weight,
        distance_weight = args.distance_weight,
    )

    return lambda perm : plan_generator.make([perm])


if __name__ == '__main__':
    main()
