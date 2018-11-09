import math
import numpy as np

# Basic firefly algorythm
def firefly(*, x, distance, I, alpha, beta, gamma, epsilon):

    new_x = x
    for i in range(len(x)):
        for j in range(i):

            # print("|{:3}| j:[{:3}]({:+7.3f},{:+7.3f}) i:[{:3}]({:+7.3f},{:+7.3f})".format(
            #     i_gen,
            #     j, x[j], I(x[j]),
            #     i, x[i], I(x[i]),
            # ), end='')
            
            if I(x[i]) > I(x[j]):
                new_x[i] += beta * math.exp(-gamma * np.power(distance(x[i], x[j]), 2)) * (x[j] - x[i]) + alpha * epsilon
                #print(" -> {:+7.3f}".format(new_x[i]), end='')
            
            #print('')

    #print('')
    return new_x
