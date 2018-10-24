import numpy as np
from michalewicz import michalewicz
from plotutil import plot3d

plot3d(
    lambda x0, x1:michalewicz((x0, x1), 10),
    np.arange(0, 4, 0.25),
    np.arange(0, 4, 0.25),
).show()