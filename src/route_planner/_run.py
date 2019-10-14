#!env/bin/python
import argparse
import numpy as np
import datetime
import distances
from datetime import datetime
from attrdict import AttrDict
import pickle

import _arguments
import firefly_with_log
import route
import init
import log

def main():

    args = _arguments.parse()

    summary_file = get_summary_file_writer(args)
    args.output_args = args.n_run <= 1

    summary_file.write('#Program\tRoute Planner Summary')
    summary_file.write('#Args\t{}'.format(vars(args)))
    summary_file.write('#Summary').flush()

    path_data = route.PathData(args.input)
    calc_value = get_calc_value(args, path_data=path_data)
    lasts = {}

    for seed in range(args.seed, args.seed + args.n_run):

        args.seed = seed
        args.init_seed = (seed - args.seed) + args.init_seed
        args.output_filename = '{}/{}.txt'.format(args.output, datetime.now().strftime("%Y%m%d_%H%M%S_%f")) if args.n_run > 1 else '{}.txt'.format(args.output)

        last_ret = firefly_with_log.run(args, path_data = path_data, calc_value = calc_value)
        summary_file.write('{:0>10}\t{}\t{:>6}\t{}'.format(seed, datetime.now().strftime("%Y%m%d%H%M%S"), last_ret.c_itr, last_ret.plan_log)).flush()
        lasts[args.seed] = last_ret

    if not args.no_binary_output:
        out_bin = AttrDict()
        out_bin.args = args
        out_bin.lasts = lasts
        path = args.binary_output if args.binary_output is not None else args.output + '.pickle'
        log.prepare_directory(path)
        with open(path, mode='wb') as f:
            pickle.dump(out_bin, file = f)



def get_summary_file_writer(args):

    if args.n_run > 1 and not args.no_log_output:
        summary_file = log.FileWriter(filepath='{}/summary_{}_{}_{}.txt'.format(args.output, args.start_date, args.start_time, args.start_microsec))
    else:
        summary_file = log.FileWriter(no_out=True)

    return summary_file


def get_calc_value(args, *, path_data):

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
