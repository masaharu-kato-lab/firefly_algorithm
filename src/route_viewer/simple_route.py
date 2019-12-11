#!env/bin/python
import pickle
import argparse
import matplotlib.pyplot as plt #type:ignore
import sys
import os
import json
from world import World

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('input', type=str, help='Input binary pickle file path')
    argp.add_argument('-o', '--output', type=str, default=None, help='Output png image file path (None:default)')
    argp.add_argument('-mi', '--mapper_input', type=str, default='res/pathdata/opu.pickle', help='Input mapper pickle file path')
    argp.add_argument('-s', '--seed', type=int, help='Seed value to draw')
    argp.add_argument('-best', '--best_only', action='store_true', help='Only draws best solution')
    argp.add_argument('-worst', '--worst_only', action='store_true', help='Only draws worst solution')
    argp.add_argument('-lg', '--show_legend', action='store_true', help='show legend')
    argp.add_argument('-lgx', '--legend_px', type=float, default=0.88, help='legend position x')
    argp.add_argument('-lgy', '--legend_py', type=float, default=0.35, help='legend position y')
    argp.add_argument('-fs', '--fontsize', type=int, default=10, help='legend font size')
    args = argp.parse_args()


    world = World(args.mapper_input)

    with open(args.input, mode='rb') as f:
        out_bin = pickle.load(f)

    # if args.output is None:
    #     args.output = os.path.splitext(args.input)[0] + '_graph/{seed}.png'
    
    # with open('{}/args.json'.format(args.output), mode='w') as f:
    #     json.dump(out_bin.args.__dict__, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(', ', ': '))
    
    fstates = out_bin.final_states_by_seed

    if args.best_only:
        items = [min(fstates.items(), key=lambda kv: kv[1].best_plan.value)]
    elif args.worst_only:
        items = [max(fstates.items(), key=lambda kv: kv[1].best_plan.value)]
    elif args.seed is None:
        items = fstates.items()
    else:
        items = [(args.seed, fstates[args.seed])]

    cmap = plt.get_cmap("Set2")

    for seed, final_states in items:
        print('seed:{}'.format(seed))
        plan = final_states.best_plan

        plt.figure()
        world.plot_world()

        for i, drone in enumerate(plan.drones):
            # print('drone {}:'.format(i), end='')
            # print(drone.pos_history)
            ps = drone.pos_history
            plt.plot(
                [p[0] for p in ps],
                [p[1] for p in ps],
                color=cmap(i),
                linestyle='-',
                marker='o',
                label='drone {}'.format(i+1)
            )

            for i, p in enumerate(filter(lambda p: p != world.depot_pos, ps), 1):
                plt.annotate(i, fontsize=args.fontsize, xy=(p[0], p[1]))

        if args.show_legend:
            plt.legend(bbox_to_anchor=(args.legend_px, args.legend_py), loc='center', borderaxespad=0, fontsize=args.fontsize)
        
        plt.xticks([])
        plt.yticks([])

        if args.output:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            plt.savefig(args.output.format(seed=seed))
        else:
            plt.show()

        plt.close()


if __name__ == '__main__':
    main()
