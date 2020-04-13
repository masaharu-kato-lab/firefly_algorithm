#!env/bin/python
import argparse
import matplotlib.pyplot as plt #type:ignore
import os
from world import World

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('-o', '--output', type=str, default=None, help='Output png image file path (None:default)')
    argp.add_argument('-mi', '--mapper_input', type=str, default='res/pathdata/opu.pickle', help='Input mapper pickle file path')
    args = argp.parse_args()

    world = World(args.mapper_input)

    plt.figure()
    world.plot_world(color='#BBBBBB')
    world.plot_nodes(color='black')
    world.plot_depot(color='black', marker='*')

    plt.xticks([])
    plt.yticks([])


    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        plt.savefig(args.output)
    else:
        plt.show()

    plt.close()


if __name__ == '__main__':
    main()
