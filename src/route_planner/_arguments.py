import argparse
from datetime import datetime
import random

def parse():

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
    argp.add_argument('-tmin', '--n_min_iterate'   , type=int  , default =None    , help='Minimum number of iteration (Optional)')
    argp.add_argument('-tmax', '--n_max_iterate'   , type=int  , default =None    , help='Maximum number of iteration (Optional)')
    argp.add_argument('-nis' , '--n_itr_steady'    , type=int  , default =None    , help='Running acceptable number of iteration from last update of best individual (optional)')
    argp.add_argument('-nup' , '--n_updates'       , type=int  , default =None    , help='(Maximum) number of updates (Optional). If specified, iteration arguments (`-tmin`, `-tmax`, `nis`) are ignored.')
    argp.add_argument('-nr'  , '--n_run'           , type=int  , default=1        , help='Number of running')
    argp.add_argument('-ndr' , '--n_drones'        , type=int  , required=True    , help='Number of drones')
    argp.add_argument('-i'   , '--input'           , type=str  , default='res/pathdata/opu.pickle', help="Input pathdata pickle filepath")
    argp.add_argument('-o'   , '--output'          , type=str  , default =None    , help='Path for output log (None for default)')
    argp.add_argument('-bo'  , '--binary_output'   , type=str  , default =None    , help='Binary output path (None for default)')
    argp.add_argument('-fmi' , '--format_init'     , type=str  , default =None    , help='Format text to display initial individuals')
    argp.add_argument('-fmt' , '--format_itr'      , type=str  , default =None    , help='Format text to display individuals while iteration')
    argp.add_argument('-fmtt', '--format_terminate', type=str  , default =None    , help='Format text to message for terminate')
    argp.add_argument('-icm' , '--init_cls_method' , type=str  , default ="none"  , choices=["none", "rmed", "pamed"], help="Clustering method in initialization, 'none' for no clustering, 'rmed' (random medoids) or 'pamed' (partitioning around medoids)")
    argp.add_argument('-ibdm', '--init_bld_dist'   , type=str  , default =None    , choices=["euclid", "aster", "angle", "polar"], help="Distance method in initial building")
    argp.add_argument('-icdm', '--init_cls_dist'   , type=str  , default =None    , choices=["euclid", "aster", "angle", "polar"], help="Distance method in initial clustering (only works when clustering is available)")
    # argp.add_argument('-ibdw', '--init_bld_dist_w' , type=float, default =None    , help="Weight of distance method in initial building (only works when `--init_bld_dist` is 'polar')")
    # argp.add_argument('-icdw', '--init_cls_dist_w' , type=float, default =None    , help="Weight of distance method in initial clustering (only works when `--init_cls_dist` is 'polar')")
    argp.add_argument('-inc' , '--init_n_cls'      , type=int  , default =None    , help="Number of clusters (only works when `--init_cls_method` is not 'none')")
    argp.add_argument('-irr' , '--init_random_rate', type=float, default =0.0     , help="Rate of random generation in initialization building")
    argp.add_argument('-uja' , '--use_jordan_alpha', action='store_true'          , help="Use jordan's method in alpha step")
    argp.add_argument('-sp'  ,'--show_progress'    , action='store_true'          , help='Show progress to stderr')
    argp.add_argument('-nlo' ,'--no_log_output'    , action='store_true'          , help='Do not output log (text) file')
    argp.add_argument('-nbo' ,'--no_binary_output' , action='store_true'          , help='Do not output binary (pickle) file')
    argp.add_argument('-vb'  ,'--verbose'          , action='store_true'          , help='Whether to output details for debugging')
    argp.add_argument('-sc'  ,'--skip_check'       , action='store_true'          , help='Whether to skip check validation of permutation on each iteration')
    argp.add_argument('-io'  ,'--init_only'        , action='store_true'          , help='Run only initialization')
    argp.add_argument('-sto' ,'--stdout'           , action='store_true'          , help='Whether output results to stdout or not (output to automatically created file)')
    argp.add_argument('-nio' ,'--no_init_output'   , action='store_true'          , help='Not output initial individuls')
    args = argp.parse_args()

    if args.init_cls_method == "none":
        if args.init_n_cls is not None or args.init_cls_dist is not None:
            raise RuntimeError("`--init_cls_method` must not be 'none'.")

    if args.binary_output is not None and args.no_binary_output:
        raise RuntimeError("`--no_binary_output` specified, but `--binary_output` specified.")

    if args.init_cls_dist is None: args.init_cls_dist = 'aster'
    if args.init_bld_dist is None: args.init_bld_dist = 'aster'

    # if args.init_bld_dist != 'polar' and args.init_bld_dist_w is not None:
    #     raise RuntimeError("`--init_bld_dist_w` is not used when `--init_bld_dist` is not 'polar'")

    # if args.init_cls_dist != 'polar' and args.init_cls_dist_w is not None:
    #     raise RuntimeError("`--init_cls_dist_w` is not used when `--init_cls_dist` is not 'polar'")

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
