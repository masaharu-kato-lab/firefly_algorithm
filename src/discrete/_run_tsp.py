import tsp.file
import tsp.distance
import objects
import solution
import argparse

def main():

	argp = argparse.ArgumentParser(description='Run firefly algorithm')
	argp.add_argument('-s', '--seed'  , type=int  , default= None, help='Seed value of random')
	argp.add_argument('-n', '--number', type=int  , default=  100, help='Number of positions')
	argp.add_argument('-g', '--gamma' , type=float, default=  0.1, help='Gamma value')
	argp.add_argument('-a', '--alpha' , type=float, default=  2.0, help='Alpha value')
	argp.add_argument('-t', '--tlen'  , type=int  , default=10000, help='Number of calculation')
	argp.add_argument('-f', '--file'  , type=str  , default='res/oliver30.tsp', help='File path to .tsp file')
	args = argp.parse_args()

	(datalist, _) = tsp.file.load(args.file)

	solution.firefly_solution(
		nodes = objects.Nodes(
			coords = datalist['NODE_COORD_SECTION'],
			func_distance = tsp.distance.euclid
		),
		seed   = args.seed,
		number = args.number,
		gamma  = args.gamma,
		alpha  = args.alpha,
		tlen   = args.tlen,
	)

if __name__ == '__main__':
	main()