import numpy as np
import random
import os
from datetime import datetime
import firefly


def print_to_file(content, filepath):
    with open(filepath, mode='a') as f:
        print(content, file=f)


def print_to_stdout(content):
    print(content)


def run(args:object, *,
    nodes    : list,
    I        : callable,
    distance : callable
):

    # Set seed value of random
    if args.seed == None: args.seed = random.randrange(2 ** 32 - 1)
    np.random.seed(seed = args.seed)


    # Set output function based on argument options
    today = datetime.now()

    if args.stdout:
        print_func = print_to_stdout

    else:
        output_filename = 'out/{}/{}.txt'.format(today.strftime("%Y%m%d"), today.strftime("%H%M%S"))
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        print_func = lambda content : print_to_file(content, output_filename)


    # Output basic information
    print_func('Discrete Firefly Algorithm using TSP')
    print_func(today.strftime("%Y/%m/%d %H:%M:%S"))
    print_func('{}'.format(vars(args)))


    prev_min_id = None
    current_elasped_time = 0

    # Run firefly algorithm
    for ret in firefly.run(
        nodes         = nodes,
        seed          = args.seed,
        number        = args.number,
        gamma         = args.gamma,
        alpha         = args.alpha,
        blocked_alpha = args.blocked_alpha,
        n_gen         = args.tlen,
        I             = I,
        distance      = distance,
    ):
        if(prev_min_id != ret.min_id):
            print_func('[{:>6}] {:>6} at {:>4} [{:}] ({:8.4f} sec) na={:}'.format(
                ret.t,
                ret.min_Ix,
                ret.min_id,
                ','.join(map(str, ret.min_x)),
                current_elasped_time,
                ret.n_attracted
            ))
            current_elasped_time = 0

        prev_min_id = ret.min_id
        current_elasped_time += ret.elapsed_time

    print_func('(END)')

