import math
import numpy as np
import copy
import time
import itertools
import objects

# Firefly algorithm class
class Firefly:

    def __init__(self, *,
        x           : dict ,         # Initial positions
        nodes       : objects.Nodes, # Nodes Object
        I           : callable,      # Objective Function (Originally means light intensity of fireflies)
        distance    : callable,      # Distance Function (calcs distance between two positions)
        debug_out   : bool = False,  # Whether to output information for debugging
    ):
        self.nodes = nodes
        self.I = I
        self.Ix = None
        self.distance = distance
        self.debug_out = debug_out
        self.setX(x)


    # Set new positions
    def setX(self, x):
        self.x = x

        self.Ix = list(map(self.I, self.x))
        self.min_node = np.argmin(self.Ix)
        self.min_x  = self.x[self.min_node]
        self.min_Ix = self.Ix[self.min_node]
        

    # Calc firefly algorithm once
    def calcOnce(self, *, gamma: float, alpha: float):
        
        # New positions of fireflies
        new_x = np.copy(self.x)
        
        time_bs = 0
        time_as = 0

        count_loop = 0
        count_calc = 0

        # Repeats for all combinations of fireflies
        for i in range(len(self.x)):
            for j in range(i):

                count_loop += 1
                
                # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
                if self.Ix[i] > self.Ix[j]:

                    count_calc += 1

                    time1 = time.time()

                    new_beta_x = self.beta_step(
                        self.x[i],
                        self.x[j],
                        1 / (1 + gamma * self.distance(self.x[i], self.x[j]))
                    )

                    time2 = time.time()
                    
                    new_x[i] = self.alpha_step(new_beta_x, int(np.random.rand() * alpha + 1.0))

                    time3 = time.time()

                    time_bs += time2 - time1
                    time_as += time3 - time2

                    if(not self.is_valid(new_x[i])): raise RuntimeError('Invalid permutation.')


        # Output processing time
        if self.debug_out:
            print('beta: {:7.4f}sec, alpha: {:7.4f}sec, calc: {:>6} / {:>6}'.format(time_bs, time_as, count_calc, count_loop))

        self.setX(new_x)



    def beta_step(self, p1, p2, beta : float):

        p12 = [None] * len(p1)
        empty_nodes   = copy.copy(self.nodes.names)
        empty_indexes = copy.copy(self.nodes.indexes)
        
        # calc intersection of p1 and p2
        for i in self.nodes.indexes: # DO NOT 'for i in empty_indexes'
            if(p1[i] == p2[i]):
                p12[i] = p1[i]
                empty_nodes.remove(p12[i])
                empty_indexes.remove(i)


        # fill empty indexes in p12
        for i in empty_indexes:

            # choose candidate node from p1's node or p2's based on beta value
            candidate_node = p1[i] if(np.random.rand() > beta) else p2[i]

            # fill with chosen candidate node if it doesn't already exist in p12
            if(candidate_node in empty_nodes):
                p12[i] = candidate_node
                empty_nodes.remove(candidate_node)
                empty_indexes.remove(i)


        if(len(empty_nodes)):

            # fill empty indexes randomly
            shuffled_empty_nodes = np.random.permutation(list(empty_nodes))
            for i, p12_i in enumerate(empty_indexes):
                p12[p12_i] = shuffled_empty_nodes[i]


        return p12



    def alpha_step(self, p, alpha : int):

        # print('alpha:{:}'.format(alpha))

        if(alpha <= 1): return p

        # alpha 個の index を shuffle する
        target_indexes = np.random.choice(self.nodes.indexes, alpha)
        shuffled_target_indexes = np.random.permutation(target_indexes)

        # shuffle target indexes
        new_p = np.copy(p)
        for shuffled_index, index in zip(shuffled_target_indexes, target_indexes):
            new_p[shuffled_index] = p[index]

        #print('a1:', new_p)
        return new_p


    # check validity
    def is_valid(self, perm):
        nodes = copy.copy(self.nodes.names)
        for p in perm:
            if(p in nodes):
                nodes.remove(p)
            else:
                return False

        if len(nodes):
            return False

        return True

