import numpy as np
import random
import os
from datetime import datetime
import firefly


def current_time_text():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

def print_to_file(content, filepath, *, date=False):
    with open(filepath, mode='a') as f:
        if date:
            print('{}\t{}'.format(current_time_text(), content), file=f)
        else:
            print(content, file=f)


def print_to_stdout(content, *, date=False):
    if date:
        print('{}\t{}'.format(current_time_text(), content))
    else:
        print(content)



def run(args:object, *,
    nodes    : list,
    I        : callable,
    distance : callable,
    x        : list = None,
    format_x    : str,
    format_init : str,
    format_calc : str,
    format_output_filename : str,
):


    # Set seed value of random
    if args.seed == None: args.seed = random.randrange(2 ** 32 - 1)
    np.random.seed(seed = args.seed)


    # Set output function based on argument options
    today = datetime.now()

    if args.stdout:
        print_func = print_to_stdout

    else:
        output_filename = format_output_filename.format(
            date = today.strftime("%Y%m%d"),
            time = today.strftime("%H%M%S"),
            datetime = current_time_text(),
        )
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        print_func = lambda content, *, date=False : print_to_file(content, output_filename, date=date)


    # Output basic information
    print_func('#Program\tDiscrete Firefly Algorithm')
    print_func('', date=True)
    print_func('#Args\t{}'.format(vars(args)))

    print_func('#Initialization')

    for i, cx in enumerate(x):
        print_func(format_init.format(
            i = i,
            Ix = I(cx),
            x = ' '.join(map(lambda _x : format_x.format(x=_x), cx))
        ))

    
    current_elasped_time = 0
    prev_min_x = np.array([None] * len(nodes))
    prev_min_Ix = float('inf')
    best_min_Ix = float('inf')

    print_func('#Iterations')

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
        fill_norandom = args.fill_norandom,
    ):
        if not np.array_equal(prev_min_x, ret.min_x):
            
            print_func(format_calc.format(
                t         = ret.t,
                diff_type = 'v' if prev_min_Ix > ret.min_Ix else '^' if prev_min_Ix < ret.min_Ix else '=',
                is_min    = '*' if best_min_Ix > ret.min_Ix else '.',
                Ix        = ret.min_Ix,
                x         = ' '.join(map(lambda x : format_x.format(x = x), ret.min_x)),
                time      = current_elasped_time
            ), date=True)
            current_elasped_time = 0

            if best_min_Ix > ret.min_Ix:
                best_min_Ix = ret.min_Ix

        prev_min_x = ret.min_x
        prev_min_Ix = ret.min_Ix
        current_elasped_time += ret.elapsed_time

    print_func('(END)', date=True)
