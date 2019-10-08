#!env/bin/python
import argparse
import numpy as np
import random
import datetime

import firefly_with_log
import route
import init

def main():

    # Parse arguments
    argp = argparse.ArgumentParser(description='Run OPU firefly algorithm')
    argp.add_argument('-s'   , '--seed'         , type=int  , default =None , help='Seed value for random in calculation')
    argp.add_argument('-is'  , '--init_seed'    , type=int  , default =None , help='Seed value for random in initialization')
    argp.add_argument('-nff' , '--n_firefly'    , type=int  , required=True , help='Number of fireflies')
    argp.add_argument('-g'   , '--gamma'        , type=float, required=True , help='Gamma value (beta-step coefficient)')
    argp.add_argument('-a'   , '--alpha'        , type=float, required=True , help='Alpha value (alpha-step coefficient)')
    argp.add_argument('-ba'  , '--blocked_alpha', type=float, default =None , help='Alpha value on fireflies are blocked (Default for do nothing)')
    argp.add_argument('-sw'  , '--safety_weight', type=float, required=True , help='Weight value of safety on objective function')
    argp.add_argument('-mind', '--min_distance' , type=float, default=10000 , help='Assumed minimum distance of permutation')
    argp.add_argument('-maxd', '--max_distance' , type=float, default=20000 , help='Assumed maximum distance of permutation')
    argp.add_argument('-t'   , '--n_iterate'    , type=int  , required=True , help='Number of iteration')
    argp.add_argument('-nr'  , '--n_run'        , type=int  , default=1     , help='Number of running')
    argp.add_argument('-ndr' , '--n_drones'     , type=int  , required=True , help='Number of drones')
    argp.add_argument('-i'   , '--input'        , type=str  , default='res/pathdata/opu.pickle', help="Input pathdata pickle filepath")
    argp.add_argument('-o'   , '--output'       , type=str  , default =None , help='Path for output log (Default for auto)')

    argp.add_argument('-icm' , '--init_clustering_method', type=str  , default =None , choices=["rm", "pam"], help="Initialization clustering method (None for no clustering, 'rm' (random medoids) or 'pam' (partitioning around medoids))")
    argp.add_argument('-inc' , '--init_n_cluster'        , type=int  , default =None , help="Number of clusters when `--init_clustering` is 'k-medoids'")
    argp.add_argument('-innr', '--init_nn_rate', type=float, default =0    , help="Rate of nodes using nearest neighbor when building path")

    argp.add_argument('-q' ,'--quiet'      , action='store_true'       , help='Do not show progress to stderr')
    argp.add_argument(      '--verbose'    , action='store_true'       , help='Whether to output details for debugging')
    argp.add_argument(      '--unsafe'     , action='store_true'       , help='Whether to check validation of permutation on each iteration')
    argp.add_argument(      '--init_only'  , action='store_true'       , help='Run only initialization')
    argp.add_argument(      '--stdout'     , action='store_true'       , help='Whether output results to stdout or not (output to automatically created file)')
    argp.add_argument(      '--result_only', action='store_true'       , help='Output only final results to stdout')
    args = argp.parse_args()

    # Load coordinates and nodes
    path_data = route.PathData(args.input)
    nodes = path_data.nodes
    dist_func = path_data.distance
    
    drone_prop = route.DroneProperty(path_data)
    plan_prop = route.PlanProperty(
        path_data = path_data,
        drone_prop = drone_prop,
        n_drones = args.n_drones,
        safety_weight = args.safety_weight,
        min_distance = args.min_distance,
        max_distance = args.max_distance,
    )



    best_plan = None
    today = datetime.datetime.now()

    if not args.output:
        args.output = 'out/{date}/{datetime}'.format(
            date = today.strftime("%Y%m%d"),
            datetime = today.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        )

    for i_run in range(args.n_run):

        x = init.generate(
            nodes = path_data.nodes,
            n_firefly = args.n_firefly,
            clustering_method = args.init_clustering_method,
            n_cluster = args.init_n_cluster,
            nn_rate = args.init_nn_rate,
            dist_func = dist_func
        )

        # print(x)
        # exit()　

        make_plan = lambda perm : route.Plan(plan_prop, [perm])

        c_best_plan = firefly_with_log.run(
            args,
            nodes = nodes,
            x = x,
            make_plan = make_plan,
            format_x_elm = '{elm:>2}',
            format_init = '{i:>6}\t{plan_value:12.8f}\t{plan_log}',
            format_calc = '{t:>6}\t{plan_value:12.8f}\t{plan_log}',
            output_filename = '{}/{:>4}.txt'.format(args.output, i_run) if args.n_run > 1 else '{}.txt'.format(args.output)
        )

        if best_plan is None or c_best_plan < best_plan:
            best_plan = c_best_plan

    return best_plan


if __name__ == '__main__':
    main()