#!env/bin/python
import argparse
import numpy as np
import random
import datetime
import distances

import firefly_with_log
import route
import init

def main():

    # Parse arguments
    argp = argparse.ArgumentParser(description='Run OPU firefly algorithm')
    argp.add_argument('-s'   , '--seed'           , type=int  , default =None , help='Seed value for random in calculation')
    argp.add_argument('-is'  , '--init_seed'      , type=int  , default =None , help='Seed value for random in initialization')
    argp.add_argument('-ni'  , '--n_indiv'        , type=int  , required=True , help='Number of individual (firefly)')
    argp.add_argument('-g'   , '--gamma'          , type=float, required=True , help='Gamma value (beta-step coefficient)')
    argp.add_argument('-a'   , '--alpha'          , type=float, required=True , help='Alpha value (alpha-step coefficient)')
    argp.add_argument('-ba'  , '--blocked_alpha'  , type=float, default =None , help='Alpha value on fireflies are blocked (Default for do nothing)')
    argp.add_argument('-sw'  , '--safety_weight'  , type=float, default=10000 , help='Weight value of safety on objective function')
    argp.add_argument('-dw'  , '--distance_weight', type=float, default=1     , help='Weight value of distance on objective function')
    # argp.add_argument('-mind', '--min_distance'   , type=float, default=10000 , help='Assumed minimum distance of permutation')
    # argp.add_argument('-maxd', '--max_distance'   , type=float, default=20000 , help='Assumed maximum distance of permutation')
    argp.add_argument('-t'   , '--n_iterate'      , type=int  , required=True , help='Number of iteration')
    argp.add_argument('-nr'  , '--n_run'          , type=int  , default=1     , help='Number of running')
    argp.add_argument('-ndr' , '--n_drones'       , type=int  , required=True , help='Number of drones')
    argp.add_argument('-i'   , '--input'          , type=str  , default='res/pathdata/opu.pickle', help="Input pathdata pickle filepath")
    argp.add_argument('-o'   , '--output'         , type=str  , default =None , help='Path for output log (Default for auto)')

    argp.add_argument('-ibm' , '--init_building_method'  , type=str  , default ="random", choices=["random", "ann", "cpnn"], help="Building method in initialization ('random' for random, 'ann' (all nearest neighbor), 'cpnn' (cluster-patterned nearest neighbor))")
    argp.add_argument('-icm' , '--init_clustering_method', type=str  , default ="none"  , choices=["none", "rm", "pam"], help="Clustering method in initialization (only works when `--init_building_method` is not 'random') ('none' for no clustering, 'rm' (random medoids) or 'pam' (partitioning around medoids))")
    argp.add_argument('-idm' , '--init_distance_method'  , type=str  , default ="aster" , choices=["euclid", "aster", "angle"], help="Distance method in initialization (only works when clustering is available)")
    argp.add_argument('-inc' , '--init_n_cluster'        , type=int  , default =None    , help="Number of clusters (only works when `--init_clustering_method` is not 'none')")
    argp.add_argument('-ibnr', '--init_building_nn_rate' , type=float, default =0       , help="Rate of nodes using nearest neighbor in initialization building (only works when `--init_building_method` is 'ann')")
    argp.add_argument('-ice' , '--init_clustering_each'  , action='store_true'          , help="Do clustering before each building (only works when `--init_building_method` is 'random' or 'ann')")
    
    argp.add_argument('-q' ,'--quiet'      , action='store_true'       , help='Do not show progress to stderr')
    argp.add_argument(      '--verbose'    , action='store_true'       , help='Whether to output details for debugging')
    argp.add_argument(      '--unsafe'     , action='store_true'       , help='Whether to check validation of permutation on each iteration')
    argp.add_argument(      '--init_only'  , action='store_true'       , help='Run only initialization')
    argp.add_argument(      '--stdout'     , action='store_true'       , help='Whether output results to stdout or not (output to automatically created file)')
    argp.add_argument(      '--result_only', action='store_true'       , help='Output only final results to stdout')
    args = argp.parse_args()


    if args.init_seed == None: args.init_seed = random.randrange(2 ** 32 - 1)
    if args.seed == None: args.seed = random.randrange(2 ** 32 - 1)

    # Load coordinates and nodes
    path_data = route.PathData(args.input)
    nodes = path_data.nodes
    
    drone_prop = route.DroneProperty(path_data)
    plan_prop = route.PlanProperty(
        path_data = path_data,
        drone_prop = drone_prop,
        n_drones = args.n_drones,
        safety_weight = args.safety_weight,
        distance_weight = args.distance_weight,
        # min_distance = args.min_distance,
        # max_distance = args.max_distance,
    )

    if args.init_distance_method == "aster":
        dist_func = path_data.distance
    elif args.init_distance_method == "angle":
        dist_func = lambda v1, v2: distances.angle_distance(v1, v2, path_data.home_poses[0])
    elif args.init_distance_method == "euclid":
        dist_func = distance.euclid

    best_plan = None
    today = datetime.datetime.now()

    if not args.output:
        args.output = 'out/{date}/{datetime}'.format(
            date = today.strftime("%Y%m%d"),
            datetime = today.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        )

    for i_run in range(args.n_run):
        
        x = init.generate(args, nodes = path_data.nodes, dist = dist_func)
        if not len(x): raise RuntimeError('Initialization failed.')

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
