import numpy as np

# ref: https://www.sfu.ca/~ssurjano/michal.html

def michalewicz(x, m):

    if(np.isscalar(x)):
        if(x < 0 or x >= np.pi):
            return np.inf
        len_range = np.arange(1, 2)
    else:
        for cx in x:
            if(cx < 0 or cx >= np.pi):
                return np.inf
        len_range = np.arange(1, len(x)+1)

#    if(np.isscalar(x)):
    ret = -sum(np.sin(x) * np.sin((len_range * x ** 2) / np.pi) ** (2 * m))
    # else:
    #     len_range = np.arange(1, len(x)+1)
    #     ret = -sum(
    #         np.multiply(
    #             np.sin(x),
    #             np.power(
    #                 np.sin(np.divide(np.multiply(len_range,  np.power(x, 2)), np.pi)),
    #                 2 * m
    #             )
    #         )
    #     )

    return ret
    