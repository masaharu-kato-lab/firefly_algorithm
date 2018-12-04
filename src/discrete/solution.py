from pprint import pprint
import numpy as np
import random
import firefly
import distance
import time

def firefly_solution(*,
	nodes  : object,        # Nodes object
	seed   : int = None,    # seed value (None for random)
	number : int,			# number of fireflies
	gamma  : float,			# variable gamma
	alpha  : float,         # variable alpha
	tlen   : int,           # length of calculation
	verbose : bool = False, # verbose flag
	print_func : callable,		# function for output results
	):

	# Set seed value of random
	if seed == None: seed = random.randrange(2 ** 32 - 1)
	np.random.seed(seed = seed)
	print_func('seed = {}'.format(seed))

	x = [0] * number
	for i in range(len(x)): x[i] = np.random.permutation(nodes.names)

	ffproc = firefly.Algorithm(
		x = x,
		nodes = nodes.names,
		distance = distance.hamming,
		I = lambda p : nodes.distance(p),
		verbose = verbose
	)

	# Run firefly algorithm
	t = 0
	prev_min_node = None
	sum_elasped_time = 0

	while(t < tlen):

		start_time = time.time()

		ffproc.calcOnce(gamma = gamma, alpha = alpha)

		elapsed_time = time.time() - start_time
		sum_elasped_time += elapsed_time

		if(prev_min_node != ffproc.min_node):
			print_func('[{:>8}] {:>9} at {:>6} [{:}] ({:7.4f} sec)'.format(t, ffproc.getMinIx(), ffproc.getMinNode(), ','.join(map(str, ffproc.getMinX())) , sum_elasped_time))
			sum_elasped_time = 0


		prev_min_node = ffproc.min_node

		t = t + 1


	print_func('(END)')
