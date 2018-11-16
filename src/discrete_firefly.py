import math
import numpy as np
import distance 
from copy import deepcopy
import time
import itertools
from tsp.nodes import Nodes

class Firefly:

    def __init__(self, *,
        x           : dict ,         # Initial positions
        nodes       : Nodes,         # Nodes Object
        I           : callable,      # Objective Function (Originally means light intensity of fireflies)
        debug_out   : bool = False,  # Whether to output information for debugging
    ):
        self.nodes = nodes
        self.I = I
        self.Ix = None
        self.debug_out = debug_out

        self.x = x
        self.aggregate()



    # Calc firefly algorithm once
    def calcOnce(self, *,
        gamma    : float,         # Constant Gamma
        alpha    : float,         # Constant Alpha
    ) -> list: # Returns positions of fireflies after calculation
        
        # New positions of fireflies
        new_x = deepcopy(self.x)
        
        time_bv = 0
        time_bs = 0
        time_as = 0

        # Repeats for all combinations of fireflies
        for i in range(len(self.x)):
            for j in range(i):
                
                # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
                if self.Ix[i] > self.Ix[j]:
                    time0 = time.time()

                    beta = 1 / (1 + gamma * distance.hamming(self.x[i], self.x[j]))

                    time1 = time.time()

                    new_beta_x = self.beta_step(self.x[i], self.x[j], beta)

                    time2 = time.time()
                    
                    new_x[i] = self.alpha_step(new_beta_x, int(np.random.rand() * alpha + 1.0))

                    time3 = time.time()

                    time_bv += time1 - time0
                    time_bs += time2 - time1
                    time_as += time3 - time2


        # Output processing time
        print({'bv': time_bv, 'bs':time_bs, 'as':time_as})

        self.x = new_x
        self.aggregate()


    def aggregate(self):
        self.Ix = list(map(self.I, self.x))
        min_index = np.argmin(self.Ix)
        self.min_x = self.x[min_index]
        self.min_Ix = self.I(self.min_x)


    def intersection(self, p, q):

        if(len(p) != len(q)): raise RuntimeError('Invalid length of permutations')

        r = [None] * len(p)
        remain_nodes = deepcopy(self.nodes.names)
        remain_indexes = list(range(len(p)))

        for i, (cp, cq, cr) in enumerate(zip(p, q, r)):
            if(cp == cq):
                cr = cp
                remain_nodes.remove(cr)
                remain_indexes.remove(i)
        
        return (r, remain_nodes, remain_indexes)
        


    def beta_step(self, p1, p2, beta : float):

        (p12, remain_nodes, remain_indexes) = self.intersection(p1, p2)

        if self.debug_out:
            print('p12:', p12, ', rn:', remain_nodes, ', ri:', remain_indexes)

        for i, (cp12, cp1, cp2) in enumerate(zip(p12, p1, p2)):
            if(cp12 != None): continue

            candidate = cp1 if(np.random.rand() > beta) else cp2

            if(candidate in remain_nodes):
                cp12 = candidate
                remain_nodes.remove(candidate)
                remain_indexes.remove(i)


        if(len(remain_indexes) != len(remain_nodes)): raise RuntimeError('Invalid remain nodes and indexes')

        if(len(remain_nodes)):
            shuffled_remain_nodes = np.random.permutation(list(remain_nodes))
            for cindex, cnode in zip(remain_indexes, shuffled_remain_nodes):
                p12[cindex] = cnode

        return p12



    def alpha_step(self, p, alpha : int):

        return self.alpha_step_internal(
            p, 
            np.random.permutation(self.nodes.indexes)[0:alpha]
        )



    def alpha_step_internal(self, p, target_indexes : list):

    #    if len(target_indexes) <= 1: return p

        new_p = deepcopy(p)

        shuffled_target_indexes = np.random.permutation(target_indexes)

        if self.debug_out:
            print('target_indexes:', target_indexes, ', shuffled_target_indexes:', shuffled_target_indexes)

        for shuffled_index, index in zip(shuffled_target_indexes, target_indexes):
            new_p[shuffled_index] = p[index]
            
        if self.debug_out:
            print('alpha p12 :', new_p)

        return new_p

