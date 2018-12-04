import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def plot2d(func, x):
    fx = list(map(func, x))
    plt.plot(x, fx)
    # plt.show()
    return plt


def plot3d(func, x0, x1):
    xx0, xx1 = np.meshgrid(x0, x1)

    y = np.zeros((len(x0), len(x1)))
    for i0 in range(len(x0)):
        for i1 in range(len(x1)):
            y[i0, i1] = func(x0[i0], x1[i1])
            
    subp = plt.subplot(1, 1, 1, projection='3d')
    subp.plot_surface(xx0, xx1, y)
    subp.set_xlabel("x0")
    subp.set_ylabel("x1")
    subp.set_zlabel("f(x0, x1)")

    # subplot.view_init(60,40)
    plt.show()
    return plt