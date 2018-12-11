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
    distance : callable,
    x        : list = None,
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
    print_func('Discrete Firefly Algorithm')
    print_func(today.strftime("%Y/%m/%d %H:%M:%S"))
    print_func('{}'.format(vars(args)))


    for i, cx in enumerate(x):
        print_func('{:>3}: {:12.4f} at [{}]'.format(i, I(cx), ' '.join(map(lambda _x : '{:>2}'.format(_x), cx))))


    current_elasped_time = 0
    prev_min_x = np.array([None] * len(nodes))
    prev_min_Ix = float('inf')
    best_min_Ix = float('inf')

    # Run firefly algorithm
    for ret in firefly.run(
        nodes         = nodes,
        seed          = args.seed,
        number        = args.number,
        x             = x,
        gamma         = args.gamma,
        alpha         = args.alpha,
        blocked_alpha = args.blocked_alpha,
        n_gen         = args.tlen,
        I             = I,
        distance      = distance,
        unsafe        = args.unsafe,
        sorting       = not args.nosort,
    ):
        if not np.array_equal(prev_min_x, ret.min_x):
            
            print_func('[{:>6}] {} {}{:12.4f} at [{}] ({:8.4f} sec)'.format(
                ret.t,
                'v' if prev_min_Ix > ret.min_Ix else '^' if prev_min_Ix < ret.min_Ix else '=',
                '*' if best_min_Ix > ret.min_Ix else '.',
                ret.min_Ix,
                ' '.join(map(lambda x : '{:>2}'.format(x), ret.min_x)),
                current_elasped_time
            ))
            current_elasped_time = 0

            if best_min_Ix > ret.min_Ix:
                best_min_Ix = ret.min_Ix

        prev_min_x = ret.min_x
        prev_min_Ix = ret.min_Ix
        current_elasped_time += ret.elapsed_time

    print_func('(END)')

