import numpy as np

def michalewicz(x, m):
    if(np.isscalar(x)):
        ret = -np.sin(x) * np.sin(x ** 2 / np.pi) ** (2 * m)
    else:
        len_range = np.arange(1, len(x)+1)
        ret = -sum(
            np.multiply(
                np.sin(x),
                np.power(
                    np.sin(np.divide(np.multiply(len_range,  np.power(x, 2)), np.pi)),
                    2 * m
                )
            )
        )
    return ret
    