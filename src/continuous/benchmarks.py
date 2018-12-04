import numpy as np

# ref: https://www.sfu.ca/~ssurjano/michal.html

# calc michalewicz function
def michalewicz(x, m : float):

    dimentions = np.arange(1, (1 if np.isscalar(x) else len(x))+1)
    ret = -sum(np.sin(x) * np.sin((dimentions * x ** 2) / np.pi) ** (2 * m))

    return ret
