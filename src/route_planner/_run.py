#!env/bin/python
import argparse
import numpy as np
import random
import datetime
import distances
from datetime import datetime

import firefly_with_log
import route
import init
import log

def main():

    # Parse arguments
    argp = argparse.ArgumentParser(description='Run OPU firefly algorithm')
    argp.add_argument('-s'   , '--seed'            , type=int  , default =None    , help='Seed value for random in calculation')
    argp.add_argument('-is'  , '--init_seed'       , type=int  , default =None    , help='Seed value for random in initialization')
    argp.add_argument('-ni'  , '--n_indiv'         , type=int  , required=True    , help='Number of individual (firefly)')
    argp.add_argument('-g'   , '--gamma'           , type=float, required=True    , help='Gamma value (beta-step coefficient)')
    argp.add_argument('-a'   , '--alpha'           , type=float, required=True    , help='Alpha value (alpha-step coefficient)')
    argp.add_argument('-ba'  , '--blocked_alpha'   , type=float, default =None    , help='Alpha value on fireflies are blocked (Default: equals to normal alpha)')
    argp.add_argument('-sw'  , '--safety_weight'   , type=float, default=10000    , help='Weight value of safety on objective function')
    argp.add_argument('-dw'  , '--distance_weight' , type=float, default=1        , help='Weight value of distance on objective function')
    # argp.add_argument('-mind', '--min_distance'  , type=float, default=10000    , help='Assumed minimum distance of permutation')
    # argp.add_argument('-maxd', '--max_distance'  , type=float, default=20000    , help='Assumed maximum distance of permutation')
    argp.add_argument('-tmin', '--n_min_iterate'   , type=int  , default =None    , help='Minimum number of iteration (Optional)')
    argp.add_argument('-tmax', '--n_max_iterate'   , type=int  , default =100000  , help='Maximum number of iteration (Optional)')
    argp.add_argument('-nis' , '--n_itr_steady'    , type=int  , default =100     , help='Running acceptable number of iteration from last update of best individual (optional)')
    argp.add_argument('-ris' , '--rate_itr_steady' , type=float, default =2.0     , help='Running acceptable increase rate of iteration from last update of best individual (optional)' )
    argp.add_argument('-nr'  , '--n_run'           , type=int  , default=1        , help='Number of running')
    argp.add_argument('-ndr' , '--n_drones'        , type=int  , required=True    , help='Number of drones')
    argp.add_argument('-i'   , '--input'           , type=str  , default='res/pathdata/opu.pickle', help="Input pathdata pickle filepath")
    argp.add_argument('-o'   , '--output'          , type=str  , default =None    , help='Path for output log (Default for auto)')
    argp.add_argument('-ibm' , '--init_bld_method' , type=str  , default ="cpnn"  , choices=["rnn", "cpnn"], help="Building method in initialization, 'rnn' (mix of random generation and nearest neighbor), 'cpnn' (cluster-patterned nearest neighbor)")
    argp.add_argument('-icm' , '--init_cls_method' , type=str  , default ="none"  , choices=["none", "rmed", "pamed"], help="Clustering method in initialization, 'none' for no clustering, 'rmed' (random medoids) or 'pamed' (partitioning around medoids)")
    argp.add_argument('-ibdm' , '--init_bld_dist'  , type=str  , default ="aster" , choices=["euclid", "aster", "angle"], help="Distance method in initialization (only works when clustering is available)")
    argp.add_argument('-icdm' , '--init_cls_dist'  , type=str  , default ="aster" , choices=["euclid", "aster", "angle"], help="Distance method in initialization (only works when clustering is available)")
    argp.add_argument('-inc' , '--init_n_cls'      , type=int  , default =None    , help="Number of clusters (only works when `--init_cls_method` is not 'none')")
    argp.add_argument('-ibnr', '--init_bld_nn_rate', type=float, default =0       , help="Rate of nodes using nearest neighbor in initialization building (only works when `--init_bld_method` is 'rnn')")
    argp.add_argument('-ice' , '--init_cls_each'   , action='store_true'          , help="Do clustering before each building (only works when `--init_bld_method` is 'random' or 'ann')")
    argp.add_argument('-sp'  ,'--show_progress'    , action='store_true'          , help='Show progress to stderr')
    argp.add_argument(        '--verbose'          , action='store_true'          , help='Whether to output details for debugging')
    argp.add_argument(        '--unsafe'           , action='store_true'          , help='Whether to check validation of permutation on each iteration')
    argp.add_argument(        '--init_only'        , action='store_true'          , help='Run only initialization')
    argp.add_argument(        '--stdout'           , action='store_true'          , help='Whether output results to stdout or not (output to automatically created file)')
    argp.add_argument(        '--result_only'      , action='store_true'          , help='Output only final results to stdout')
    args = argp.parse_args()


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

    ccoef_mint  = (lambda idv: idv.c_itr < args.n_min_iterate) if args.n_min_iterate is not None else lambda idv: False
    ccoef_maxt  = (lambda idv: idv.c_itr < args.n_max_iterate) if args.n_max_iterate else lambda idv: True

    if args.n_itr_steady or args.rate_itr_steady:
        ccoef_nis  = (lambda idv: (idv.c_itr - idv.best_itr) < args.n_itr_steady) if args.n_itr_steady else lambda idv: False
        ccoef_ris  = (lambda idv: idv.prev_best_itr is None or (idv.c_itr - idv.best_itr) < (idv.best_itr - idv.prev_best_itr) * args.rate_itr_steady) if args.rate_itr_steady else lambda idv: False

        continue_coef = lambda idv: ccoef_mint(idv) or (ccoef_maxt(idv) and (ccoef_nis(idv) or ccoef_ris(idv)))

    else:
        continue_coef = lambda idv: ccoef_mint(idv) or ccoef_maxt(idv)


    best_plan = None
    today = datetime.now()

    if not args.output:
        args.output = 'out/{date}/{datetime}'.format(
            date = today.strftime("%Y%m%d"),
            datetime = today.strftime("%Y%m%d%H%M%S"),
        )

    if args.n_run > 1:
        summary_filepath = '{}/summary.txt'.format(args.output)
        log.prepare_directory(summary_filepath)
        print_to_summary = lambda *args, datetime = False: log.print_to_file(*args, filepath = summary_filepath, datetime = datetime)
    else:
        print_to_summary = lambda *args, datetime = None: None

    print_to_summary(
        '#Program\tRoute Planner Summary',
        '#Args\t{}'.format(vars(args))
    )
    print_to_summary('#Summary', datetime=True)

    if args.seed == None: args.seed = random.randrange(2 ** 32 - 1)
    if args.init_seed == None: args.init_seed = args.seed

    for seed in range(args.seed, args.seed + args.n_run):
        
        x = init.generate(args, path_data = path_data)
        if not len(x): raise RuntimeError('Initialization failed.')

        make_plan = lambda perm : route.Plan(plan_prop, [perm])

        args.seed = seed
        args.init_seed = (seed - args.seed) + args.init_seed

        last_ret = firefly_with_log.run(
            args,
            nodes = nodes,
            x = x,
            continue_coef = continue_coef,
            make_plan = make_plan,
            format_x_elm = '{elm:>2}',
            format_init = '{i:>6}\t{v:9.2f}\t{sv:9.6f}\t{dv:9.2f}\t{log}',
            format_calc = '{t:>6}\t{v:9.2f}\t{sv:9.6f}\t{dv:9.2f}\t{log}',
            output_filename = '{}/{:0>10}.txt'.format(args.output, seed) if args.n_run > 1 else '{}.txt'.format(args.output)
        )

        print_to_summary('{:0>10}\t{}\t{:>6}\t{}'.format(
            seed,
            datetime.now().strftime("%Y%m%d%H%M%S"),
            last_ret.c_itr,
            last_ret.plan_log
        ))

        if best_plan is None or last_ret.best_plan < best_plan:
            best_plan = last_ret.best_plan


    print_to_summary('#END', datetime=True)
    print_to_summary('#EOF')

    return best_plan


if __name__ == '__main__':
    main()
