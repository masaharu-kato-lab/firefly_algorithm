from datetime import datetime
import os
import random
import sys

from attrdict import AttrDict #type:ignore
import numpy as np #type:ignore

import firefly
import log
import init
import route

from typing import Callable, Dict, List, Tuple
Node = Tuple[int, int]
Value = route.Plan

def run(args, *,
    path_data  : route.PathData,
    calc_value : Callable,
) -> Dict[int, AttrDict]:

    logfile = make_logfile_writer(args)

    # Output basic information
    logfile.write('#Program\tRoute Planner')
    logfile.write('#Args\t{}'.format(vars(args)))

    indivs:List[List[Node]] = init.generate(args, path_data = path_data)
    val_of = list(map(calc_value, indivs))

    if not args.no_init_output:
        logfile.write('#Initialization')
        output_values(args, val_of, logfile)
        logfile.write('#END').flush()

    if not args.init_only:
        logfile.write('#Iterations')
        states = optimize(args, logfile, nodes=path_data.nodes, calc_value=calc_value, init_indivs=indivs, init_val_of=val_of)
        logfile.write('#END')
    
    logfile.write('#EOF').flush()

    return states



def optimize(
    args,
    logfile  : log.FileWriter,
    *,
    nodes    : List[Node],
    calc_value: Callable,
    init_indivs : List[List[Node]],
    init_val_of : List[Value],
) -> Dict[int, AttrDict]:

    np.random.seed(seed = args.seed)

    states:Dict[int, AttrDict] = {}

    # Run firefly algorithm
    for state in firefly.run(
        nodes            = nodes,
        init_indivs      = init_indivs,
        init_val_of      = init_val_of,
        calc_value       = calc_value,
        continue_coef    = make_continue_coef(args),
        gamma            = args.gamma,
        alpha            = args.alpha,
        blocked_alpha    = args.blocked_alpha,
        skip_check       = args.skip_check,
        use_jordan_alpha = args.use_jordan_alpha,
    ):  
        states[state.itr] = state
        
        if state.itr == state.best_itr:
            
            logfile.write(args.format_itr.format(
                t    = state.itr,
                nu   = state.n_updated,
                v    = state.best_plan.value,
                sv   = state.best_plan.average_safety,
                dv   = state.best_plan.total_distance,
                log  = state.best_plan.text,
            )).flush()

        if args.show_progress and state.itr % 10 == 0:
            print('.', file=sys.stderr, end='')
            sys.stderr.flush()

    logfile.write(args.format_terminate.format(t = state.itr))
        
    if args.show_progress:
        print('', file=sys.stderr)

    return states



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

    if args.n_itr_steady:
        check_steady = lambda idv: (idv.itr - idv.best_itr) < args.n_itr_steady
        if args.n_min_iterate:
            if args.n_max_iterate:
                if args.n_min_iterate > args.n_max_iterate:
                    raise RuntimeError('Maximum iteration is smaller than minimum iteration.')
                return lambda idv: idv.itr <= args.n_min_iterate or (idv.itr <= args.n_max_iterate and check_steady(idv))
            return lambda idv: idv.itr <= args.n_min_iterate or check_steady(idv)
        if args.n_max_iterate:
            return lambda idv: idv.itr <= args.n_max_iterate and check_steady(idv)
        return lambda idv: check_steady(idv)
    else:
        if args.n_min_iterate:
            return lambda idv: idv.itr <= args.n_min_iterate
        if args.n_max_iterate:
            return lambda idv: idv.itr <= args.n_max_iterate
    
    raise RuntimeError('All of minimum and maximum and steady iterations are not specified.')



def make_logfile_writer(args):

    if args.no_log_output:
        if args.stdout: return log.FileWriter(outobj=sys.stdout)
        return log.FileWriter(no_out=True)

    if args.stdout: return log.FileWriter(filepath=args.output_filename, outobj=sys.stdout)
    return log.FileWriter(filepath=args.output_filename)

