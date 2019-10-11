import pickle
import argparse
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('-i', '--input', type=str, required=True, help='Input binary pickle file.')
    args = argp.parse_args()

    with open(args.input, mode='rb') as f:
        out_bin = pickle.load(f)

    for seed, last_ret in out_bin.lasts.items():
        print('seed:{}'.format(seed))
        plan = last_ret.best_plan

        for i, drone in enumerate(plan.drones):
            # print('drone {}:'.format(i), end='')
            # print(drone.pos_history)
            ps = drone.pos_history
            plt.plot(
                [p[0] for p in ps],
                [p[1] for p in ps],
                label='drone {}:'.format(i)
            )
        
        plt.show()
    

if __name__ == '__main__':
    main()
