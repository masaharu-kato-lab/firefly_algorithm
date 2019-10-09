import numpy as np
import random
import os
import sys
from datetime import datetime

import firefly
import log

from typing import List, Dict, Tuple
Node = Tuple[int, int]


def run(args, *,
    nodes         : List[Node],
    make_plan     : callable,
    x             : List[List[Node]],
    continue_coef : callable,
    format_x_elm: str,
    # legend_init : str,
    # legend_calc : str,
    format_init : str,
    format_calc : str,
    output_filename : str,
):

    
    # Set output function based on argument options
    today = datetime.now()

    if args.stdout:
        print_to_log = log.print_to_stdout

    elif not args.result_only:
        output_filepath = output_filename.format(
            date = today.strftime("%Y%m%d"),
            time = today.strftime("%H%M%S"),
            datetime = log.current_time_text(),
        )
        log.prepare_directory(output_filepath)
        print_to_log = lambda *args, datetime = False: log.print_to_file(*args, filepath = output_filepath, datetime = datetime)

    else:
        print_to_log = lambda *args, datetime = None: None

    if not args.result_only:
        # Output basic information
        print_to_log(
            '#Program\tRoute Planner',
            '#Args\t{}'.format(vars(args))
        )

        print_to_log('#Initialization', datetime=True)

        # print_to_log(legend_init)

        for i, cx in enumerate(x):
            plan = make_plan(cx)
            print_to_log(format_init.format(
                i    = i,
                v    = plan.value,
                sv   = plan.average_safety,
                dv   = plan.total_distance,
                log  = plan.text
            ))

        print_to_log('#END', datetime=True)


    if not args.init_only:

        # Set seed value of random
        np.random.seed(seed = args.seed)
        
        # current_elasped_time = 0

        if not args.result_only:
            print_to_log('#Iterations', datetime=True)

        # print_to_log(legend_calc)
        last_ret = None

        # Run firefly algorithm
        for ret in firefly.run(
            nodes         = nodes,
            x             = x,
            gamma         = args.gamma,
            alpha         = args.alpha,
            blocked_alpha = args.blocked_alpha,
            make_plan     = make_plan,
            unsafe        = args.unsafe,
            continue_coef = continue_coef,
        ):
            if ret.c_itr == ret.best_itr:
                
                if not args.result_only:
                    last_plan_log = format_calc.format(
                        t    = ret.c_itr,
                        v    = ret.best_plan.value,
                        sv   = ret.best_plan.average_safety,
                        dv   = ret.best_plan.total_distance,
                        log  = ret.best_plan.text,
                        # time = current_elasped_time
                    )
                    print_to_log(last_plan_log)

                # current_elasped_time = 0

            if args.show_progress: # and not args.result_only:
                print('.', file=sys.stderr, end='')
                sys.stderr.flush()

            last_ret = ret
            # current_elasped_time += ret.elapsed_time

        if not args.result_only:
            print_to_log('{t:>6}\t#END'.format(t = last_ret.c_itr), datetime=True)
            
        if args.show_progress:
            print('', file=sys.stderr)

    if not args.result_only:
        print_to_log('#EOF')
    else:
        print(last_ret.text)


    last_ret.plan_log = last_plan_log

    return last_ret

