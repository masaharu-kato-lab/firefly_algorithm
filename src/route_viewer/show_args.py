#!env/bin/python
import pickle
import argparse
import json
import sys
import os
sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary arguments checker')
    argp.add_argument('input', type=str, help='Input binary pickle file path')
    args = argp.parse_args()

    with open(args.input, mode='rb') as f:
        out_bin = pickle.load(f)
        print(out_bin.args)


if __name__ == '__main__':
    main()
