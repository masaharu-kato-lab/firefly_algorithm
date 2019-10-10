import numpy as np
import random
import os
import sys
from datetime import datetime

import firefly
import log
import init
import route

from typing import List, Dict, Tuple
Node = Tuple[int, int]
Value = route.Plan

def run(args, *,
    path_data  : route.PathData,
    calc_value : callable,
):

    logfile = make_logfile_writer(args)

    # Output basic information
    logfile.write('#Program\tRoute Planner')
    if args.output_args: logfile.write('#Args\t{}'.format(vars(args)))

    indivs = init.generate(args, path_data = path_data)
    val_of = list(map(calc_value, indivs))

    if not args.no_init_output:
        logfile.write('#Initialization')
        output_values(args, val_of, logfile)
        logfile.write('#END').flush()


    if not args.init_only:
        logfile.write('#Iterations')
        last_ret = optimize(args, logfile, nodes=path_data.nodes, calc_value=calc_value, init_indivs=indivs, init_val_of=val_of)
        logfile.write('#END')
    
    logfile.write('#EOF').flush()
    if args.print_result:
        print(last_ret.text)

    return last_ret



def optimize(
    args,
    logfile  : log.FileWriter,
    *,
    nodes    : List[Node],
    calc_value: callable,
    init_indivs : List[List[Node]],
    init_val_of : List[Value],
):

    np.random.seed(seed = args.seed)

    last_ret = None

    # Run firefly algorithm
    for ret in firefly.run(
        nodes         = nodes,
        init_indivs   = init_indivs,
        init_val_of   = init_val_of,
        calc_value    = calc_value,
        continue_coef = make_continue_coef(args),
        gamma         = args.gamma,
        alpha         = args.alpha,
        blocked_alpha = args.blocked_alpha,
        skip_check    = args.skip_check,
    ):
        if ret.c_itr == ret.best_itr:
            
            last_plan_log = args.format_itr.format(
                t    = ret.c_itr,
                v    = ret.best_plan.value,
                sv   = ret.best_plan.average_safety,
                dv   = ret.best_plan.total_distance,
                log  = ret.best_plan.text,
                # time = current_elasped_time
            )
            logfile.write(last_plan_log).flush()

            # current_elasped_time = 0

        if args.show_progress and ret.c_itr % 10 == 0:
            print('.', file=sys.stderr, end='')
            sys.stderr.flush()

        last_ret = ret

    logfile.write('{t:>6}\t#terminated.'.format(t = last_ret.c_itr))
        
    if args.show_progress:
        print('', file=sys.stderr)

    
    last_ret.plan_log = last_plan_log

    return last_ret



def output_values(args, val_of:list, logfile:log.FileWriter):

    for i, val in enumerate(val_of):
        logfile.write(args.format_init.format(
            i    = i,
            v    = val.value,
            sv   = val.average_safety,
            dv   = val.total_distance,
            log  = val.text
        ))


def make_continue_coef(args):

    ccoef_mint  = (lambda idv: idv.c_itr < args.n_min_iterate) if args.n_min_iterate is not None else lambda idv: False
    ccoef_maxt  = (lambda idv: idv.c_itr < args.n_max_iterate) if args.n_max_iterate else lambda idv: True

    if args.n_itr_steady or args.rate_itr_steady:
        ccoef_nis  = (lambda idv: (idv.c_itr - idv.best_itr) < args.n_itr_steady) if args.n_itr_steady else lambda idv: False
        ccoef_ris  = (lambda idv: idv.prev_best_itr is None or (idv.c_itr - idv.best_itr) < (idv.best_itr - idv.prev_best_itr) * args.rate_itr_steady) if args.rate_itr_steady else lambda idv: False

        continue_coef = lambda idv: ccoef_mint(idv) or (ccoef_maxt(idv) and (ccoef_nis(idv) or ccoef_ris(idv)))

    else:
        continue_coef = lambda idv: ccoef_mint(idv) or ccoef_maxt(idv)

    return continue_coef



def make_logfile_writer(args):

    if args.no_log_output:
        if args.stdout: return log.FileWriter(outobj=sys.stdout)
        return log.FileWriter(no_out=True)

    if args.stdout: return log.FileWriter(filepath=args.output_filename, outobj=sys.stdout)
    return log.FileWriter(filepath=args.output_filename)

