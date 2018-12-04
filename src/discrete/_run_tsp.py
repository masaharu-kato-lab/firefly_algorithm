import tsp.file
import tsp.distance
import objects
import solution
import argparse
import os
from datetime import datetime


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


	today = datetime.now()

	if args.stdout:
		print_func = print_to_stdout

	else:
		output_filename = 'out/{}/{}.txt'.format(today.strftime("%Y%m%d"), today.strftime("%H%M%S"))
		os.makedirs(os.path.dirname(output_filename), exist_ok=True)
		print_func = lambda content : print_to_file(content, output_filename)


	print_func('Discrete Firefly Algorithm using TSP')
	print_func(today.strftime("%Y/%m/%d %H:%M:%S"))
	print_func('{}'.format(vars(args)))


	(datalist, _) = tsp.file.load(args.file)

	solution.firefly_solution(
		nodes = objects.Nodes(
			coords = datalist['NODE_COORD_SECTION'],
			func_distance = tsp.distance.euclid
		),
		seed    = args.seed,
		number  = args.number,
		gamma   = args.gamma,
		alpha   = args.alpha,
		tlen    = args.tlen,
		verbose = args.verbose,
		print_func = print_func
	)



if __name__ == '__main__':
	main()
