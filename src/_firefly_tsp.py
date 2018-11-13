import tsp.file
import tsp.distance
from pprint import pprint
import numpy as np
import random
import discrete_firefly as df
from datetime import datetime

# Load nodes and coordinates from tsp file
(datalist, options) = tsp.file.load('res/oliver30.tsp')

coords = datalist['NODE_COORD_SECTION']
nodes = list(coords)



# Set seed value of random
seed = random.randrange(2 ** 32 - 1)
np.random.seed(seed=seed)

n = 100
x = df.sample(nodes, n)

I = lambda p : tsp.distance.calc(coords, p, tsp.distance.euclid)


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
	x = df.firefly(
		x = x,
		I = I,
		alpha = 15.0,
		gamma = 1.0,
	)
	
	Ix = list(map(I, x))
	min_x_i = np.argmin(Ix)

	with open(output_filename, mode='a') as f:
		print('[{:>8}] {:>9} at'.format(t, I(x[min_x_i])), x[min_x_i], file=f)

	t = t + 1
