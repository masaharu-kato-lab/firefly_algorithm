from pprint import pprint
import numpy as np
import random
import algorithm
import distance
from datetime import datetime
import time

def firefly_solution(*,
	nodes  : object,
	seed   : int = None,
	number : int,
	gamma  : float,
	alpha  : float,
	tlen   : int
	):

	# Set seed value of random
	if seed == None: seed = random.randrange(2 ** 32 - 1)
	np.random.seed(seed = seed)

	x = [0] * number
	for i in range(len(x)): x[i] = np.random.permutation(nodes.names)

	ffproc = algorithm.Firefly(
		x = x,
		nodes = nodes,
		distance = distance.hamming,
		I = lambda p : nodes.distance(p)
	)


	today = datetime.now()
	output_filename = 'out/output_{:}.txt'.format(today.strftime("%Y%m%d%H%M%S"))

	with open(output_filename, mode='a') as f:
		print('Discrete Firefly Algorithm using TSP', file=f)
		print(today.strftime("%Y/%m/%d %H:%M:%S"), file=f)
		print('seed   : {:}'.format(seed  ), file=f)
		print('number : {:}'.format(number), file=f)
		print('gamma  : {:}'.format(gamma ), file=f)
		print('alpha  : {:}'.format(alpha ), file=f)
		print('tlen   : {:}'.format(tlen  ), file=f)



	# Run firefly algorythm
	t = 0
	prev_min_node = None
	sum_elasped_time = 0

	while(t < tlen):

		start_time = time.time()

		ffproc.calcOnce(gamma = gamma, alpha = alpha)

		elapsed_time = time.time() - start_time
		sum_elasped_time += elapsed_time

		with open(output_filename, mode='a') as f:
			if(prev_min_node != ffproc.min_node):
				print('[{:>8}] {:>9} at {:>6} [{:}] ({:7.4f} sec)'.format(t, ffproc.min_Ix, ffproc.min_node, ','.join(map(str, ffproc.min_x)) , sum_elasped_time), file = f)
				sum_elasped_time = 0


		prev_min_node = ffproc.min_node

		t = t + 1


	with open(output_filename, mode='a') as f:
		print('(END)', file = f)
