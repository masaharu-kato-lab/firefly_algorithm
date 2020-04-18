#!env/bin/python
import argparse
from datetime import datetime
import os
import pickle
import sys

from attrdict import AttrDict #type:ignore
import numpy as np #type:ignore

import _arguments
import build
import clustering
import distances
import firefly
import log
import permutation
import route

from typing import Callable, Dict, List, Optional, Tuple
Node = Tuple[int, int]
Value = route.Plan



def main():

    try:
        args = _arguments.parse()
    except RuntimeError as e:
        print('Argument Error: {}'.format(e))
        return -1


    pathdata = route.PathData(args.input)
    calc_value = get_calc_value(args, pathdata=pathdata)
    init_p_perms_by_seed:Dict[int, List[build.PatternedPermutation]] = {}
    states_by_seed  :Dict[int, Dict[int, AttrDict]] = {}
    bests_by_seed   :Dict[int, List[Value]] = {}
    variants_by_seed:Dict[int, List[int]] = {}

    start_seed = args.seed
    start_init_seed = args.init_seed

    for seed in range(start_seed, start_seed + args.n_run):

        args.seed = seed
        args.init_seed = (seed - start_seed) + start_init_seed
        args.output_filename = '{}/{}.txt'.format(args.output, datetime.now().strftime("%Y%m%d_%H%M%S_%f")) if args.n_run > 1 else '{}.txt'.format(args.output)

        init_p_perms_by_seed[args.seed], states_by_seed[args.seed], bests_by_seed[args.seed], variants_by_seed[args.seed] \
             = run(args, pathdata = pathdata, calc_value = calc_value)


    if not args.no_binary_output:
        out_bin = AttrDict()
        out_bin.args = args
        out_bin.init_p_perms_by_seed = init_p_perms_by_seed
        out_bin.states_by_seed = states_by_seed
        out_bin.final_states_by_seed = {seed:list(states.items())[-1][1] for seed, states in states_by_seed.items()}
        out_bin.bests_by_seed = bests_by_seed
        out_bin.variants_by_seed = variants_by_seed

        path = args.binary_output if args.binary_output is not None else args.output + '.pickle'
        log.prepare_directory(path)
        with open(path, mode='wb') as f:
            pickle.dump(out_bin, file = f)



def run(args, *,
    pathdata  : route.PathData,
    calc_value : Callable,
) -> Dict[int, AttrDict]:

    logfile = make_logfile_writer(args)

    # Output basic information
    logfile.write('#Program\tRoute Planner')
    logfile.write('#Args\t{}'.format(vars(args)))

    init_p_perms:List[build.PatternedPermutation] = init(args, pathdata = pathdata)
    init_indivs = [p_perm.nodes for p_perm in init_p_perms]
    val_of = list(map(calc_value, init_indivs))

    if not args.no_init_output:
        logfile.write('#Initialization')
        output_values(args, init_p_perms, val_of, logfile)
        logfile.write('#END').flush()

    if not args.init_only:
        logfile.write('#Iterations')
        states, bests_by_update, variants_by_update = optimize(args, logfile, nodes=pathdata.nodes, calc_value=calc_value, init_indivs=init_indivs, init_val_of=val_of)
        logfile.write('#END')
    
    logfile.write('#EOF').flush()

    return init_p_perms, states, bests_by_update, variants_by_update



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

    bests_by_update:List[Value] = []
    variants_by_update:List[int] = []

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
        bests_out        = bests_by_update,
        variants_out     = variants_by_update,
    ):  
        states[state.itr] = state
        
        if state.best_is_updated:
            
            logfile.write(args.format_itr.format(
                t    = state.itr,
                nup  = state.n_updates,
                v    = state.best_plan.value,
                sv   = state.best_plan.average_safety,
                dv   = state.best_plan.total_distance,
                log  = state.best_plan.text,
            )).flush()

        if args.show_progress and state.itr % 10 == 0:
            print('.', file=sys.stderr, end='')
            sys.stderr.flush()

    logfile.write(args.format_terminate.format(t = state.itr, nup = state.n_updates))
        
    if args.show_progress:
        print('', file=sys.stderr)

    return states, bests_by_update, variants_by_update



def init(args, *, pathdata:route.PathData) -> List[build.PatternedPermutation]:

    np.random.seed(seed = args.init_seed)

    bld_dist = distances.get_func(args.init_bld_dist, pathdata = pathdata) # , w_angle=args.init_bld_dist_w
    cls_dist = distances.get_func(args.init_cls_dist, pathdata = pathdata) # , w_angle=args.init_cls_dist_w

    n_random = round(args.init_random_rate * args.n_indiv)
    n_special = args.n_indiv - n_random

    if n_random < 0 or n_special < 0 or n_random + n_special != args.n_indiv:
        raise RuntimeError('Invalid number of individuals.')

    init_p_perms:List[build.PatternedPermutation] = []

    # Random generation
    for _ in range(n_random):
        init_p_perms.append(build.build_randomly(pathdata.nodes))

    # Cluster-patterned generation
    if n_special:
        clusters_nodes = clustering.get_function(method = args.init_cls_method, nodes = pathdata.nodes, n_cluster = args.init_n_cls, dist = cls_dist)()

        if args.init_bld_method == 'rg':
            builder = build.Builder(methods_func_dof = {
                'R': (lambda nodes: build.build_randomly(nodes), 1),
                'G': (lambda nodes: build.build_greedy(nodes, bld_dist, nn_n_random=args.init_greedy_rnum, start_node=pathdata.home_poses[0]), 0),
            }, clusters_nodes = clusters_nodes)
            init_p_perms.extend(builder.build_with_dof(n_special))

        elif args.init_bld_method == 'r':
            for _ in range(n_special):
                init_p_perms.append(build.chain_patterned_permutations([build.build_randomly(c_nodes) for c_nodes in clusters_nodes]))

        else:
            raise RuntimeError('Unknown initialzation building method.')


    # Validation
    if not all([permutation.is_valid(p_perm.nodes, pathdata.nodes) for p_perm in init_p_perms]):
        raise RuntimeError('Invalid individuals.')

    return init_p_perms



def get_calc_value(args, *, pathdata:route.PathData) -> Callable:

    plan_generator = route.PlanGenerator(
        pathdata = pathdata,
        drone_prop = route.DroneProperty(pathdata),
        n_drones = args.n_drones,
        safety_weight = args.safety_weight,
        distance_weight = args.distance_weight,
    )

    return lambda perm : plan_generator.make([perm])



def output_values(args, init_p_perms:List[build.PatternedPermutation], val_of:list, logfile:log.FileWriter):

    for i, (p_perm, val) in enumerate(zip(init_p_perms, val_of)):
        logfile.write(args.format_init.format(
            i    = i,
            v    = val.value,
            sv   = val.average_safety,
            dv   = val.total_distance,
            log  = val.text,
            pat  = pattern_to_str(p_perm.pattern)
        ))


def pattern_to_str(pattern):
    if isinstance(pattern, tuple):
        return '(' + ' '.join(map(pattern_to_str, pattern)) + ')'

    if isinstance(pattern, str):
        return pattern
    
    raise RuntimeError('Invalid pattern type.')


def make_continue_coef(args):

    if args.n_updates:
        return lambda idv: idv.n_updates <= args.n_updates

    if args.n_iterates:
        return lambda idv: idv.itr <= args.n_iterates
    
    raise RuntimeError('No termination terms are specified.')



def make_logfile_writer(args):

    if args.no_log_output:
        if args.stdout: return log.FileWriter(outobj=sys.stdout)
        return log.FileWriter(no_out=True)

    if args.stdout: return log.FileWriter(filepath=args.output_filename, outobj=sys.stdout)
    return log.FileWriter(filepath=args.output_filename)



if __name__ == '__main__':
    main()
