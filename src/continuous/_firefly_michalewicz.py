import firefly
import benchmarks
import matplotlib.pyplot as plt
import random
import sys
import numpy as np
import subprocess

# Set seed value of random
seed = random.randrange(2 ** 32 - 1)
print('seed: {:}'.format(seed))
np.random.seed(seed=seed)

n = 100
I = lambda x: benchmarks.michalewicz(x, 10)
# I = lambda x: x ** 4 - 20 * x ** 2 + 20 * x
# sd = 5.0
# x = np.random.normal(0, sd, n)
# x = np.random.rand(n) * 2.0 - 1.0
x = np.random.rand(n) * np.pi
print(x)

# Run firefly algorythm
for t in range(100):
	x = firefly.algorithm(
		x = x,
		distance = lambda p, q: np.linalg.norm(q - p),
		I = I,
		alpha = 1.0,
		beta = 1.0,
		gamma = 1.0,
		epsilon = np.random.normal(0, 2.0),
	)
	
	Ix = list(map(I, x))
	min_x_i = np.argmin(Ix)
	print('[{:>4}] {:+9.6f} at {:+f}'.format(t, I(x[min_x_i]), x[min_x_i]))

#	print('[{0:>4}] {1:+9.6f} at ({2[0]:+f}, {2[1]:+f})'.format(
#		t, I(x[min_x_i]), x[min_x_i])
#	)

	#input()
