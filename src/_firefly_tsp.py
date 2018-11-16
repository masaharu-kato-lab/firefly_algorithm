import tsp.file
import tsp.distance
from pprint import pprint
import numpy as np
import random
import discrete_firefly
from datetime import datetime
import time
from tsp.nodes import Nodes

# Load nodes and coordinates from tsp file
(datalist, options) = tsp.file.load('res/oliver30.tsp')

nodes = Nodes(
	coords = datalist['NODE_COORD_SECTION'],
	func_distance = tsp.distance.euclid
)


# Set seed value of random
# seed = random.randrange(2 ** 32 - 1)
seed = 2405767257
np.random.seed(seed=seed)

n = 100
I = lambda p : nodes.distance(p)

x = [0] * nodes.length
for i in range(len(x)): x[i] = np.random.permutation(nodes.names)

ffproc = discrete_firefly.Firefly(
	x = x,
	nodes = nodes,
	I = I,
#	debug_out= True,
)


today = datetime.now()
output_filename = 'out/output_{:}.txt'.format(today.strftime("%Y%m%d%H%M%S"))

with open(output_filename, mode='a') as f:
	print('Discrete Firefly Algorithm using TSP', file=f)
	print(today.strftime("%Y/%m/%d %H:%M:%S"), file=f)
	print('seed: {:}'.format(seed), file=f)
	print('n: {:}'.format(n), file=f)



# Run firefly algorythm
t = 0
while(True):
	start_time = time.time()

	ffproc.calcOnce(
		gamma = 0.1,
		alpha = 2.0
	)

	elapsed_time = time.time() - start_time

	with open(output_filename, mode='a') as f:
		print(
			'[{:>8}] {:>9} at'.format(t, ffproc.min_Ix),
			ffproc.min_x,
			' ({:7.4f} sec)'.format(elapsed_time),
			file = f
		)

	t = t + 1
