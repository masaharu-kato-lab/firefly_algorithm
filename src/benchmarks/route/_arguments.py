import argparse
from datetime import datetime
import random

def parse():

    # Parse arguments
    argp = argparse.ArgumentParser(description='Run route optimization using Firefly Algorithm')
    argp.add_argument('-nr'   , '--n_run'           , type=int  , default=1        , help='Number of running')
    argp.add_argument('-i'    , '--input'           , type=str  , default='res/pathdata/opu.pickle', help="Input pathdata pickle filepath")
    argp.add_argument('-o'    , '--output'          , type=str  , default =None    , help='Path for output (None for default)')
    argp.add_argument('-v'    , '--verbose'         , action='store_true'          , help='Whether to output details for debugging')
    argp.add_argument('-pvn'  , '--p_vehicle_n'     , type=int  , required=True    , help='Number of drones')
    argp.add_argument('-psw'  , '--p_safety_w'      , type=float, default=10000    , help='Weight value of safety on objective function')
    argp.add_argument('-pdw'  , '--p_dist_w'        , type=float, default=1        , help='Weight value of distance on objective function')
    argp.add_argument('-is'   , '--init_seed'       , type=int  , default =None    , help='Seed value for initialization')
    argp.add_argument('-icm'  , '--icls_method'     , type=str  , default ='none'  , choices=['none', 'rmed', 'pamed'], help="Clustering method in initialization, 'none' for no clustering, 'rmed' (random medoids) or 'pamed' (partitioning around medoids)")
    argp.add_argument('-icn'  , '--icls_n'          , type=int  , default =None    , help="Number of clusters (only works when `--init_cls_method` is not 'none')")
    argp.add_argument('-icdm' , '--icls_dist'       , type=str  , default =None    , choices=['aster', 'euclid', 'aster_euclid', 'angle', 'polar'], help="Distance method in initial clustering (only works when clustering is available)")
    argp.add_argument('-icas' , '--icls_a_sdist'    , action='store_true'          , help='Allow same distance between nodes (select randomly) in initial clustering')
    argp.add_argument('-ibm'  , '--ibld_method'     , type=str  , default ='rg'    , choices=['r', 'rg'], help="Building method in initialization, 'r' for no random only, 'rg' for both random and greedy.")
    argp.add_argument('-ibdm' , '--ibld_dist'       , type=str  , default =None    , choices=['aster', 'euclid', 'aster_euclid', 'angle', 'polar'], help="Distance method in initial building")
    argp.add_argument('-ibrr' , '--ibld_random_rate', type=float, default =0.0     , help="Rate of random generation in initialization building")
    argp.add_argument('-ibgrn', '--ibld_greedy_rnum', type=int  , default =0       , help='Number of nodes which is generated randomly in the greedy arrangement in initial building')
    argp.add_argument('-fnu'  , '--ff_n_updates'    , type=int  , required=True    , help='Number of updates')
    argp.add_argument('-fs'   , '--ff_seed'         , type=int  , default =None    , help='Seed value for firefly optimization')
    argp.add_argument('-fn'   , '--ff_n'            , type=int  , required=True    , help='Number of fireflies')
    argp.add_argument('-fg'   , '--ff_gamma'        , type=float, required=True    , help='Gamma value (beta-step hyper-parameter)')
    argp.add_argument('-fa'   , '--ff_alpha'        , type=float, required=True    , help='Alpha value (alpha-step hyper-parameter)')
    argp.add_argument('-fam'  , '--ff_alpha_method' , type=str  , default ='jordan', choices=['normal', 'jordan'],  help="Alpha-step shuffle method")
    args = argp.parse_args()

    if args.init_cls_method == "none":
        if args.init_n_cls is not None or args.init_cls_dist is not None:
            raise RuntimeError("`--init_cls_method` must not be 'none'.")

    if args.binary_output is not None and args.no_binary_output:
        raise RuntimeError("`--no_binary_output` specified, but `--binary_output` specified.")

    if args.init_cls_dist is None: args.init_cls_dist = 'aster_euclid'
    if args.init_bld_dist is None: args.init_bld_dist = 'aster_euclid'

    if args.n_updates is not None:
        if args.n_min_iterate is not None: raise RuntimeError('Cannot use `--n_min_iterate` with `--n_updates`.')
        if args.n_max_iterate is not None: raise RuntimeError('Cannot use `--n_max_iterate` with `--n_updates`.')
        if args.n_itr_steady  is not None: raise RuntimeError('Cannot use `--n_itr_steady` with `--n_updates`.')
    else:
        if args.n_min_iterate is None and args.n_max_iterate is None and args.n_itr_steady is None:
            raise RuntimeError('At least one of `--n_min_iterate`, `--n_max_iterate`, `--n_itr_steady`, or `--n_updates` is required.')


    today = datetime.now()
    args.start_date = today.strftime("%Y%m%d")
    args.start_time = today.strftime("%H%M%S")
    args.start_microsec = today.strftime("%f")

    if not args.output:
        args.output = 'out/{}/{}_{}_{}'.format(args.start_date, args.start_date, args.start_time, args.start_microsec)

    if args.seed == None: args.seed = random.randrange(2 ** 32 - 1)
    if args.init_seed == None: args.init_seed = args.seed


    if args.format_init      is None: args.format_init = '{i:>6}\t{pat:>13}\t{v:9.2f}\t{sv:9.6f}\t{dv:9.2f}\t{log}'
    if args.format_itr       is None: args.format_itr  = '{nbup:>6}\t{t:>6}\t{nup:>9}\t{v:9.2f}\t{sv:9.6f}\t{dv:9.2f}\t{log}'
    if args.format_terminate is None: args.format_terminate = '#Terminated on iteration {t} ({nup} updates)'

    return args
