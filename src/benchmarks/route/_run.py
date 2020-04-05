#!env/bin/python
import argparse
from datetime import datetime
import os
import pickle
import sys

import random

from src.route_planner import _arguments
from src.route_planner import generate
from src.common import arrangement
from src.common import clustering
from src.route_planner import distances
from src.common import firefly
from src.route_planner import drone_simulator

from typing import Callable, Dict, Set, List, Optional, Tuple
Node = Tuple[int, int]
Value = drone_simulator.Plan



def main():

    try:
        args = _arguments.parse()
    except RuntimeError as e:
        print('Argument Error: {}'.format(e))
        return -1


    pathdata = drone_simulator.PathData(args.input)
    calc_value = get_calc_value(args, pathdata=pathdata)
    init_p_perms_by_seed:Dict[int, List[build.PatternedPermutation]] = {}
    states_by_seed:Dict[int, Dict[int, AttrDict]] = {}

    start_seed = args.seed
    start_init_seed = args.init_seed

    for seed in range(start_seed, start_seed + args.n_run):

        args.seed = seed
        args.init_seed = (seed - start_seed) + start_init_seed
        args.output_filename = '{}/{}.txt'.format(args.output, datetime.now().strftime("%Y%m%d_%H%M%S_%f")) if args.n_run > 1 else '{}.txt'.format(args.output)

        init_p_perms_by_seed[args.seed], states_by_seed[args.seed] = run(args, pathdata = pathdata, calc_value = calc_value)


    if not args.no_binary_output:
        out_bin = AttrDict()
        out_bin.args = args
        out_bin.init_p_perms_by_seed = init_p_perms_by_seed
        out_bin.states_by_seed = states_by_seed
        out_bin.final_states_by_seed = {seed:list(states.items())[-1][1] for seed, states in states_by_seed.items()}
        
        path = args.binary_output if args.binary_output is not None else args.output + '.pickle'
        log.prepare_directory(path)
        with open(path, mode='wb') as f:
            pickle.dump(out_bin, file = f)



def run(args, *,
    pathdata  : drone_simulator.PathData,
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
        states = optimize(args, logfile, node_set=pathdata.node_set, calc_value=calc_value, init_indivs=init_indivs, init_val_of=val_of)
        logfile.write('#END')
    
    logfile.write('#EOF').flush()

    return init_p_perms, states



def optimize(
    args,
    logfile  : log.FileWriter,
    *,
    node_set : Set[Node],
    calc_value: Callable,
    init_indivs : List[List[Node]],
    init_val_of : List[Value],
) -> Dict[int, AttrDict]:

    random.seed(args.seed)

    states:Dict[int, AttrDict] = {}

    # Run firefly algorithm
    for state in discrete_firefly.run(
        node_set         = node_set,
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
                nup  = state.n_updates,
                nbup = state.n_best_updates,
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

    return states



def init(args, *, pathdata:drone_simulator.PathData) -> List[build.PatternedPermutation]:

    random.seed(args.init_seed)

    bld_dist = distances.get_function(args.init_bld_dist, pathdata = pathdata) # , w_angle=args.init_bld_dist_w
    cls_dist = distances.get_function(args.init_cls_dist, pathdata = pathdata) # , w_angle=args.init_cls_dist_w

    n_random = round(args.init_random_rate * args.n_indiv)
    n_special = args.n_indiv - n_random

    if n_random < 0 or n_special < 0 or n_random + n_special != args.n_indiv:
        raise RuntimeError('Invalid number of individuals.')

    init_p_perms:List[build.PatternedPermutation] = []

    # Random generation
    for _ in range(n_random):
        init_p_perms.append(arrangement.randomly(pathdata.nodes))

    # Cluster-patterned generation
    if n_special:
        clustering_process = clustering.Clustering(nodes = pathdata.nodes, n_cluster = args.init_n_cls, dist = cls_dist, allow_same_dist = args.allow_same_dist)

        clusters_nodes = clustering_process.get_function(args.init_cls_method)()

        if args.init_bld_method == 'rg':
            builder = build.Builder(methods_func_dof = {
                'R': (lambda nodes: arrangement.randomly(nodes), 1),
                'G': (lambda nodes: arrangement.greedy(nodes, bld_dist, nn_n_random=args.init_greedy_rnum, start_node=pathdata.home_poses[0]), 0),
            }, clusters_nodes = clusters_nodes)
            init_p_perms.extend(builder.build_with_dof(n_special))

        elif args.init_bld_method == 'r':
            for _ in range(n_special):
                init_p_perms.append(build.chain_patterned_permutations([arrangement.randomly(c_nodes) for c_nodes in clusters_nodes]))

        else:
            raise RuntimeError('Unknown initialzation building method.')


    # Validation
    if not all([permutation.is_valid(p_perm.nodes, pathdata.nodes) for p_perm in init_p_perms]):
        raise RuntimeError('Invalid individuals.')

    return init_p_perms





if __name__ == '__main__':
    main()