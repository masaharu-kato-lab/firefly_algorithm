import tsp.file
import tsp.distance
from pprint import pprint
import numpy as np
import random
import discrete_firefly as df

# Load nodes and coordinates from tsp file
(datalist, options) = tsp.file.load('res/oliver30.tsp')

coords = datalist['NODE_COORD_SECTION']
nodes = list(coords)



# Set seed value of random
seed = random.randrange(2 ** 32 - 1)
print('seed: {:}'.format(seed))
np.random.seed(seed=seed)

n = 10
x = df.sample(nodes, n)

I = lambda p : tsp.distance.calc(coords, p, tsp.distance.euclid)

# Run firefly algorythm
for t in range(100):
	x = df.firefly(
		x = x,
		I = I,
		alpha = 1.0,
		gamma = 1.0,
		epsilon = np.random.normal(0, 2.0),
	)
	
	Ix = list(map(I, x))
	min_x_i = np.argmin(Ix)
	print('[{:>4}] {:+9.6f} at {:+f}'.format(t, I(x[min_x_i]), x[min_x_i]))
