import numpy as np
import random
import os
import sys
from datetime import datetime
import firefly

from typing import List, Dict, Tuple
Node = Tuple[int, int]


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
    nodes       : List[Node],
    make_plan  : callable,
    x           : List[List[Node]],
    format_x_elm: str,
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
            i_cx = make_plan(cx)
            print_to_log(format_init.format(i = i, plan_value = i_cx.value, plan_log = i_cx.log))

        print_to_log('#END', datetime=True)


    if not args.init_only:

        # Set seed value of random
        if args.seed == None: args.seed = random.randrange(2 ** 32 - 1)
        np.random.seed(seed = args.seed)
        
        
        current_elasped_time = 0
        prev_min_x = np.array([None] * len(nodes))
        prev_best_plan = None
        best_plan = None

        if not args.result_only:
            print_to_log('#Iterations', datetime=True)

        # Run firefly algorithm
        for ret in firefly.run(
            nodes         = nodes,
            x             = x,
            gamma         = args.gamma,
            alpha         = args.alpha,
            blocked_alpha = args.blocked_alpha,
            n_iterate     = args.n_iterate,
            make_plan    = make_plan,
            unsafe        = args.unsafe
        ):
            if not np.array_equal(prev_best_plan, ret.best_plan):
                
                if not args.result_only:
                    print_to_log(format_calc.format(
                        t          = ret.t,
                        diff_type  = ' ' if prev_best_plan is None else 'v' if prev_best_plan > ret.best_plan else '^' if prev_best_plan < ret.best_plan else '=',
                        is_min     = ' ' if prev_best_plan is None else '*' if best_plan > ret.best_plan else '.',
                        plan_value = ret.best_plan.value,
                        plan_log   = ret.best_plan.log,
                        time       = current_elasped_time
                    ))
                current_elasped_time = 0

                if best_plan is None or best_plan > ret.best_plan:
                    best_plan = ret.best_plan

            if not args.quiet: # and not args.result_only:
                print('.', file=sys.stderr, end='')
                sys.stderr.flush()

            prev_best_plan = ret.best_plan
            current_elasped_time += ret.elapsed_time

        if not args.result_only:
            print_to_log('#END', datetime=True)
            
        if not args.quiet:
            print('', file=sys.stderr)

    if not args.result_only:
        print_to_log('#EOF')
    else:
        print(prev_best_plan.log)

    return prev_best_plan

