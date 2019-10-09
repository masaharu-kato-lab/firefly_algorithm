import numpy as np
import random
import os
import sys
from datetime import datetime

import firefly
import log

from typing import List, Dict, Tuple
Node = Tuple[int, int]


def run(args:object, *,
    nodes       : List[Node],
    make_plan  : callable,
    x           : List[List[Node]],
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
        
        
        current_elasped_time = 0
        prev_best_plan = None
        best_plan = None
        last_plan_log = None

        if not args.result_only:
            print_to_log('#Iterations', datetime=True)

        # print_to_log(legend_calc)

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
            if prev_best_plan is None or prev_best_plan.text != ret.best_plan.text:
                
                if not args.result_only:
                    last_plan_log = format_calc.format(
                        t    = ret.t,
                        v    = ret.best_plan.value,
                        sv   = ret.best_plan.average_safety,
                        dv   = ret.best_plan.total_distance,
                        log  = ret.best_plan.text,
                        time = current_elasped_time
                    )
                    print_to_log(last_plan_log)
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
        print(prev_best_plan.text)

    return prev_best_plan, last_plan_log

