import numpy as np
import random
import os
import sys
from datetime import datetime
import firefly


def current_time_text():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

def print_to_file(*args, filepath : str, datetime : bool = False):
    with open(filepath, mode='a') as f:
        for arg in args: print(arg, file=f)
        if datetime: print('@' + current_time_text(), file=f)


def print_to_stdout(*args, datetime : bool = False):
    for arg in args: print(arg)
    if datetime: print('@' + current_time_text())



def run(args:object, *,
    nodes    : list,
    I        : callable,
    distance : callable,
    x        : list = None,
    format_x    : str,
    format_init : str,
    format_calc : str,
    output_filename : str,
):

    # Set output function based on argument options
    today = datetime.now()

    if args.stdout:
        print_to_log = print_to_stdout

    elif not args.result_only:
        output_filepath = output_filename.format(
            date = today.strftime("%Y%m%d"),
            time = today.strftime("%H%M%S"),
            datetime = current_time_text(),
        )
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        print_to_log = lambda *args, datetime = False: print_to_file(*args, filepath = output_filepath, datetime = datetime)

    else:
        print_to_log = lambda *args : None

    if not args.result_only:
        # Output basic information
        print_to_log(
            '#Program\tDiscrete Firefly Algorithm',
            '#Args\t{}'.format(vars(args))
        )

        print_to_log('#Initialization', datetime=True)

        for i, cx in enumerate(x):
            print_to_log(format_init.format(
                i = i,
                Ix = I(cx),
                x = ' '.join(map(lambda _x : format_x.format(x=_x), cx))
            ))

        print_to_log('#END', datetime=True)


    prev_min_x = None

    if not args.init_only:

        # Set seed value of random
        if args.seed == None: args.seed = random.randrange(2 ** 32 - 1)
        np.random.seed(seed = args.seed)
        
        
        current_elasped_time = 0
        prev_min_x = np.array([None] * len(nodes))
        prev_min_Ix = float('inf')
        best_min_Ix = float('inf')

        if not args.result_only:
            print_to_log('#Iterations', datetime=True)

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
            unsafe        = args.unsafe
        ):
            if not np.array_equal(prev_min_x, ret.min_x):
                
                if not args.result_only:
                    print_to_log(format_calc.format(
                        t         = ret.t,
                        diff_type = 'v' if prev_min_Ix > ret.min_Ix else '^' if prev_min_Ix < ret.min_Ix else '=',
                        is_min    = '*' if best_min_Ix > ret.min_Ix else '.',
                        Ix        = ret.min_Ix,
                        x         = ' '.join(map(lambda x : format_x.format(x = x), ret.min_x)),
                        time      = current_elasped_time
                    ))
                current_elasped_time = 0

                if best_min_Ix > ret.min_Ix:
                    best_min_Ix = ret.min_Ix

            if not args.quiet: # and not args.result_only:
                print('.', file=sys.stderr, end='')
                sys.stderr.flush()

            prev_min_x = ret.min_x
            prev_min_Ix = ret.min_Ix
            current_elasped_time += ret.elapsed_time

        if not args.result_only:
            print_to_log('#END', datetime=True)
            
        if not args.quiet:
            print('', file=sys.stderr)

    if not args.result_only:
        print_to_log('#EOF')
    else:
        print(' '.join(map(lambda x : '{x}'.format(x = x), prev_min_x)))

    return prev_min_x

