import tsp.file
import tsp.distance
import objects
import firefly
import argparse
import os
from datetime import datetime
import distance
import random
import numpy as np


def print_to_file(content, filepath):
	with open(filepath, mode='a') as f:
		print(content, file=f)

def print_to_stdout(content):
	print(content)


def main():

	argp = argparse.ArgumentParser(description='Run firefly algorithm')
	argp.add_argument('-s', '--seed'    , type=int  , default =None , help='Seed value of random')
	argp.add_argument('-n', '--number'  , type=int  , required=True , help='Number of positions')
	argp.add_argument('-g', '--gamma'   , type=float, required=True , help='Gamma value')
	argp.add_argument('-a', '--alpha'   , type=float, required=True , help='Alpha value')
	argp.add_argument('-t', '--tlen'    , type=int  , required=True , help='Number of calculation')
	argp.add_argument('-f', '--file'    , type=str  , required=True , help='File path to .tsp file')
	argp.add_argument(      '--verbose' , action="store_true"       , help='Whether to output details for debugging')
	argp.add_argument(      '--stdout'  , action="store_true"       , help='Whether output results to stdout or not (output to automatically created file)')
	args = argp.parse_args()


	# Set seed value of random
	if args.seed == None: args.seed = random.randrange(2 ** 32 - 1)
	np.random.seed(seed = args.seed)


	# Set output function based on argument options
	today = datetime.now()

	if args.stdout:
		print_func = print_to_stdout

	else:
		output_filename = 'out/{}/{}.txt'.format(today.strftime("%Y%m%d"), today.strftime("%H%M%S"))
		os.makedirs(os.path.dirname(output_filename), exist_ok=True)
		print_func = lambda content : print_to_file(content, output_filename)


	# Output basic information
	print_func('Discrete Firefly Algorithm using TSP')
	print_func(today.strftime("%Y/%m/%d %H:%M:%S"))
	print_func('{}'.format(vars(args)))

	# Load coordinates and nodes
	(datalist, _) = tsp.file.load(args.file)

	nodes = objects.Nodes(
		coords = datalist['NODE_COORD_SECTION'],
		func_distance = tsp.distance.euclid
	)


	# Run firefly algorithm
	for ret in firefly.run(
		nodes    = nodes.names,
		seed     = args.seed,
		number   = args.number,
		gamma    = lambda _ : args.gamma,
		alpha    = lambda _ : args.alpha,
		n_gen    = args.tlen,
		I        = lambda p : nodes.distance(p),
		distance = distance.hamming,
	):
		if(ret.prev_min_id != ret.min_id):
			print_func('[{:>8}] {:>9} at {:>6} [{:}] ({:7.4f} sec)'.format(
				ret.t,
				ret.min_Ix,
				ret.min_id,
				','.join(map(str, ret.min_x)),
				ret.elapsed_time
			))

	print_func('(END)')



if __name__ == '__main__':
	main()
