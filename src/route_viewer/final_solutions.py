#!env/bin/python
import pickle
import argparse
import matplotlib.pyplot as plt
import os
import attrdict
import os
import sys
sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('input', nargs='*', type=str, help='Input binary pickle file path')
    argp.add_argument('-o', '--output' , type=str, default=None, help='Output figure file path (None to display)')
    argp.add_argument('-t', '--title', type=str, default=None, help='Title text')
    argp.add_argument('-ms', '--marker_size', type=float, default=10, help='Scatter marker size')
    argp.add_argument('-sx', '--size_x', type=float, default=12, help='Figure size x (inch)')
    argp.add_argument('-sy', '--size_y', type=float, default=8, help='Figure size y (inch)')
    argp.add_argument('-dpi', '--dpi', type=float, default=200, help='Figure DPI (pixel per inch)')
    argp.add_argument('-gl', '--group_length', type=float, default=None, help='Group length')
    args = argp.parse_args()
    
    if args.output and os.path.dirname(args.output): os.makedirs(os.path.dirname(args.output), exist_ok=True)
    cmap = plt.get_cmap("tab10")
    mmap = ['o', 'x', 's', '+', 'D', 'H', 'd', 'h', '8']
    if not args.group_length: args.group_length = len(args.input)

    plt.figure(figsize=(args.size_x, args.size_y))
    for i, cinput in enumerate(args.input):
        with open(cinput, mode='rb') as f:
            out_bin = pickle.load(f)

        rets = out_bin.lasts.values()
        plt.scatter(
            [ret.best_itr for ret in rets],
            [ret.best_plan.value for ret in rets],
            color=cmap(int(i % args.group_length)),
            marker=mmap[int(i // args.group_length)],
            label=os.path.splitext(os.path.basename(cinput))[0],
            s = args.marker_size
        )
        
    plt.legend()
    if args.title is not None:
        plt.title(args.title)

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.show()

    plt.close()


if __name__ == '__main__':
    main()
