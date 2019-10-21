#!env/bin/python
import pickle
import argparse
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from world import World
from path_counter import PathCounter
import os
import attrdict

# import sys
# import os
# sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('-i', '--input' , nargs='*', type=str, required=True, help='Input binary pickle file path')
    argp.add_argument('-o', '--output' , type=str, default=None, help='Output figure file directory (None to display)')
    argp.add_argument('-mi', '--mapper_input', type=str, default='res/pathdata/opu.pickle', help='Input mapper pickle file path')
    argp.add_argument('-sw', '--standard_width', type=float, default=5.0, help='Standard line width of path')
    argp.add_argument('-t', '--title', type=str, default=None, help='Title formatted text')
    args = argp.parse_args()
    
    world = World(args.mapper_input)
    
    if args.output: os.makedirs(args.output, exist_ok=True)

    for cinput in args.input:
        print(cinput)

        with open(cinput, mode='rb') as f:
            out_bin = pickle.load(f)

        bin_args = out_bin.args.__dict__
        path_counter = PathCounter()

        for last_ret in out_bin.lasts.values():
            for drone in last_ret.best_plan.drones:
                path_counter.add_poses(drone.pos_history)

        n_plans = len(out_bin.lasts)
        lines = LineCollection(
            list(path_counter.undirected_counter.keys()),
            linewidths=[(count / n_plans) * args.standard_width for count in path_counter.undirected_counter.values()]
        )
        
        _, ax = plt.subplots()
        world.plot_world()
        ax.add_collection(lines)
        ax.autoscale()

        if args.title is not None:
            plt.title(args.title.format(**bin_args))

        if args.output:
            plt.savefig('{}/{}.png'.format(args.output, os.path.splitext(os.path.basename(cinput))[0]))
        else:
            plt.show()

        plt.close()


if __name__ == '__main__':
    main()
