import tsp.file
import tsp.distance
import objects
import solution
import argparse

def main():

	argp = argparse.ArgumentParser(description='Run firefly algorithm')
	argp.add_argument('-s', '--seed'    , type=int  , default =None , help='Seed value of random')
	argp.add_argument('-n', '--number'  , type=int  , required=True , help='Number of positions')
	argp.add_argument('-g', '--gamma'   , type=float, required=True , help='Gamma value')
	argp.add_argument('-a', '--alpha'   , type=float, required=True , help='Alpha value')
	argp.add_argument('-t', '--tlen'    , type=int  , required=True , help='Number of calculation')
	argp.add_argument('-f', '--file'    , type=str  , required=True , help='File path to .tsp file')
	argp.add_argument('-v', '--verbose' , type=bool , default =False, help='Whether to output details for debugging')
	args = argp.parse_args()

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
		verbose = args.verbose
	)

if __name__ == '__main__':
	main()