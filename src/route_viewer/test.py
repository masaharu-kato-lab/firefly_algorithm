import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
np.random.seed(1977)

x = np.arange(10)
y = np.cos(x / np.pi)
width = 20 * np.random.random(x.shape)

# Create the line collection. Widths are in _points_!  A line collection
# consists of a series of segments, so we need to reformat the data slightly.
coords = list(zip(x, y))
lines = [(start, end) for start, end in zip(coords[:-1], coords[1:])]
lines = LineCollection(lines, linewidths=width)

fig, ax = plt.subplots()
ax.add_collection(lines)
ax.autoscale()
plt.show()