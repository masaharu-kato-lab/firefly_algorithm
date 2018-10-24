import matplotlib.pyplot as plt
import numpy as np

np.random.seed(int(input('seed:')))

n = int(input('n:'))

# ndim = int(input('ndim:'))

diffs = np.random.randn(n)
values = []
cvalue = 0

# for dim in range(ndim):
for cdiff in diffs:
    cvalue += cdiff
    values.append(cvalue)

plt.plot(range(n), values)
plt.ylabel('some numbers')
plt.show()