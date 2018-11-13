import math
import numpy as np
from typing import Callable

# Calc firefly algorithm once
def firefly(*,
        x        : list,         # Initial positions of fireflies
        distance : Callable,     # Function to calculate distance between two fireflies
        I        : Callable,     # Objective Function (Originally means light intensity of fireflies)
        alpha    : float,        # Constant Alpha
        beta     : float,        # Constant Beta
        gamma    : float,        # Constant Gamma
        epsilon  : float,        # Constant Epsilon
        debug_out : bool = False # Whether to output information for debugging
    ) -> list: # Returns positions of fireflies after calculation
    
    # New positions of fireflies
    new_x = x

    # Repeats for all combinations of fireflies
    for i in range(len(x)):
        for j in range(i):
            
            # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
            if I(x[i]) > I(x[j]):
                # Move firefly based on formula
                new_x[i] += beta * math.exp(-gamma * np.power(distance(x[i], x[j]), 2)) * (x[j] - x[i]) + alpha * epsilon

            # Output positions and intensities of fireflies for debugging
            if debug_out:
                print("     j:[{:3}]({:+7.3f},{:+7.3f}) i:[{:3}]({:+7.3f},{:+7.3f})".format(
                    j, x[j], I(x[j]),
                    i, x[i], I(x[i]),
                ), end='')

                if I(x[i]) > I(x[j]):
                    print(" -> {:+7.3f}".format(new_x[i]), end='') 
                
                print('')

        if debug_out:
            print('') 

    # Returns new positions of fireflies
    return new_x
