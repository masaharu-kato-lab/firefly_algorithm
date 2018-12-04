import numpy as np
from michalewicz import michalewicz
from plotutil import plot2d

plot2d(lambda x:michalewicz(x, 20), np.arange(-10, +10, 0.01)).show()