import tsp.file
import tsp.distance
import objects
import argparse
import distance
import output

def main():

	# Parse arguments
	argp = argparse.ArgumentParser(description='Run firefly algorithm')
	argp.add_argument('-s' , '--seed'         , type=int  , default =None , help='Seed value of random')
	argp.add_argument('-n' , '--number'       , type=int  , required=True , help='Number of positions')
	argp.add_argument('-g' , '--gamma'        , type=float, required=True , help='Gamma value')
	argp.add_argument('-a' , '--alpha'        , type=float, required=True , help='Alpha value')
	argp.add_argument('-ba', '--blocked_alpha', type=float, default =None , help='Alpha value on fireflies are blocked (Default for do nothing)')
	argp.add_argument('-t' , '--tlen'         , type=int  , required=True , help='Number of calculation')
	argp.add_argument('-f' , '--file'         , type=str  , required=True , help='File path to .tsp file')
	argp.add_argument(      '--verbose' , action="store_true"       , help='Whether to output details for debugging')
	argp.add_argument(      '--stdout'  , action="store_true"       , help='Whether output results to stdout or not (output to automatically created file)')
	args = argp.parse_args()

	# Load coordinates and nodes
	(datalist, _) = tsp.file.load(args.file)

	nodes = objects.Nodes(
		coords = datalist['NODE_COORD_SECTION'],
		func_distance = tsp.distance.euclid
	)


	return output.run(
		args,
		nodes    = nodes.names,
		I        = lambda p : nodes.distance(p),
		distance = distance.hamming
	)



if __name__ == '__main__':
	main()
