import random
import math
import distance
import copy
import argparse
import time
from sys import path
import pickle
import numpy as np

with open("res/mapper.pickle", "rb") as f:
    mapper = pickle.load(f)

class firefly:
    def __init__(self, p, eta, nb_drone):
        self.eta = eta
        self.nb_drone = nb_drone
        points = [element for element in p]
        random.shuffle(points)
        self.update(points)

    # Update fireflies data
    def update(self, x):
        uncertainty, distance, solution = self.evaluate(x)
        self.x = solution
        self.uncertainty = uncertainty
        self.distance = distance
        self.luminosity = 10000 * uncertainty + self.eta * distance

    # Build the paths from a list of points
    def evaluate(self, _coords):
        coords = [element for element in _coords]
        limit = 0
        battery = 0
        last_position = [mapper.starting_point[i] for i in range(self.nb_drone)]
        start = [p for p in last_position]
        point_time = {}
        drone_elapsed_time = [0 for i in range(self.nb_drone)]
        d = 0
        solution = []
        way = []
        while len(coords) > 0:
            if limit + mapper.paths[(last_position[d], coords[0])][1] + mapper.paths[(coords[0], start[d])][1] < 3000:
                path = mapper.paths[(last_position[d], coords[0])][1]
                limit += path
                drone_elapsed_time[d] += path * 0.5
                point_time[coords[0]] = drone_elapsed_time[d]
                way.append(coords[0])
                last_position[d] = coords.pop(0)
            else:
                solution.append(way)
                way = []
                path = mapper.paths[(last_position[d], start[d])][1]
                battery += limit + path
                limit = 0
                drone_elapsed_time[d] += path * 0.5
                last_position[d] = start[d]
                d += 1
                if d >= self.nb_drone:
                    d = 0
        for d in range(self.nb_drone):
            if last_position[d] != start[d]:
                solution.append(way)
                path = mapper.paths[(last_position[d], start[d])][1]
                battery += limit + path
                drone_elapsed_time[d] += path * 0.5
        end_patrol_time = max(drone_elapsed_time)
        mean = []
        for element in list(point_time.values()):
            mean.append(1 - math.exp(-0.001279214 * (end_patrol_time - element)))
        mean = sum(mean) / len(mean)
        return mean, battery, solution



def flatten(a):
    return [element for sublist in a for element in sublist]


# Beta step: exploitation
def betaStep(_A, _B, gamma): #move b to a

    A = flatten(_A)
    B = flatten(_B)
    C = [None] * len(A)
    beta = 1 / (1 + gamma * distance.hamming(A, B))
    remains = copy.copy(A)
    remain_indexes = list(range(len(A)))
    visited = {i:False for i in A}

    for i in range(len(C)):
        if A[i] == B[i]:
            C[i] = A[i]
            visited[C[i]] = True
            remains.remove(C[i])
            remain_indexes.remove(i)



    for i in remain_indexes:
        if random.random() < beta:
            if not visited[A[i]]:
                C[i] = A[i]
                remains.remove(A[i])
                visited[A[i]] = True

            elif not visited[B[i]]:
                C[i] = B[i]
                remains.remove(B[i])
                visited[B[i]] = True

        else:
            if not visited[B[i]]:
                C[i] = B[i]
                remains.remove(B[i])
                visited[B[i]] = True

            elif not visited[A[i]]:
                C[i] = A[i]
                remains.remove(A[i])
                visited[A[i]] = True


    random.shuffle(remains)


    for value in remains:
        C[C.index(None)] = value


    return C



# Alpha step: exploration (v1)
def alphaStep1(a, alpha):
    for i in range(alpha):
        x = random.randint(0, len(a)-1)
        y = random.randint(0, len(a)-1)
        a[x], a[y] = a[y], a[x]
    return a

# Alpha step: exploration (v2)
def alphaStep2(a, alpha):
    idxs = [i for i in range(len(a))]
    random.shuffle(idxs)
    x = idxs[0:alpha]
    y = idxs[0:alpha]
    random.shuffle(y)
    for i in range(alpha):
        a[x[i]],  a[y[i]] = a[y[i]], a[x[i]]
    return a

# Alpha step: exploration (v3)
def alphaStep3(a, alpha):
    A = [element for element in a]
    random.shuffle(A)
    B = [element for element in a]
    C = ['' for i in A]
    to_insert = [i for i in A]
    for i in range(len(A)):
        if A[i] == B[i] or random.random() < alpha:
            if A[i] not in C:
                C[i] = A[i]
                to_insert.remove(A[i])
        else:
            if B[i] not in C:
                C[i] = B[i]
                to_insert.remove(B[i])
    while len(to_insert) > 0:
        idx = C.index('')
        C[idx] = to_insert.pop()
    return C


# Firefly algorithm
def fireflyAlgorithm(z, args):

    if args.verbose: print(args)

    points = [(32, 1122), (271, 1067), (209, 993), (184, 1205), (303, 1220), (400, 1122), (505, 1214), (669, 1202), (779, 1026), (912, 1029), (1483, 1156), (1614, 991), (1576, 567), (1502, 395), (1618, 227), (1448, 634), (967, 690), (1059, 842), (759, 823), (1387, 174), (1073, 82), (944, 327), (866, 512), (748, 638), (487, 896), (118, 653), (35, 902), (502, 339), (683, 316), (694, 123), (45, 52), (367, 39)]
    swarm = [firefly(points, args.dist_penal_coef, args.n_drones) for i in range(args.n_fireflies)]
    swarm = sorted(swarm, key = lambda ff: ff.luminosity)
    best_firefly = copy.deepcopy(swarm[0])

    if args.verbose: print("Best firefly init: ", best_firefly.luminosity)

    t = 0
    n = len(swarm)
    start_time = time.time()

    while t < args.n_iteration:
        for i in range(n):
            for j in range(n):
                if j != i:
                    if swarm[j].luminosity < swarm[i].luminosity:
                        C = betaStep(swarm[j].x, swarm[i].x, args.gamma)
                        if args.alpha_ver == 1:
                            C = alphaStep1(C, args.alpha)
                        elif args.alpha_ver == 2:
                            C = alphaStep2(C, args.alpha)
                        elif args.alpha_ver == 3:
                            C = alphaStep3(C, args.alpha)

                        swarm[i].update(C)

        swarm = sorted(swarm, key = lambda ff: ff.luminosity)
        if swarm[0].luminosity == swarm[-1].luminosity: #If all the fireflies are at the same position

            if args.verbose: print("*** swarm blocked ***")

            for i in range(1, len(swarm)):
                C = [element for subList in swarm[i].x for element in subList]

                if args.alpha_ver == 1:
                    C = alphaStep1(C, args.alpha)
                elif args.alpha_ver == 2:
                    C = alphaStep2(C, args.alpha)
                elif args.alpha_ver == 3:
                    C = alphaStep3(C, args.alpha)
                swarm[i].update(C)
                
            swarm = sorted(swarm, key = lambda ff: ff.luminosity)

        if best_firefly.luminosity > swarm[0].luminosity:
            best_firefly = copy.deepcopy(swarm[0])
            
        if args.verbose and t % 10 == 0:
            print("[{:>4}] Best firefly: {}".format(t, best_firefly.luminosity))

        t += 1

    endTime = time.time()

    if args.verbose:
        print("Elapsed time: ", endTime - start_time)

    return best_firefly



if __name__ == "__main__":
    # Arguments
    argp = argparse.ArgumentParser()
    argp.add_argument('-d', '--n_drones'        , type = int  , default = 2         , help = 'number of drones')
    argp.add_argument('-t', '--n_iteration'     , type = int  , default = 3000      , help = 'number of iterations')
    argp.add_argument('-g', '--gamma'           , type = float, default = 0.90      , help = 'firefly algorithm gamma')
    argp.add_argument('-a', '--alpha'           , type = int  , default = 1         , help = 'firefly algorithm alpha')
    argp.add_argument('-n', '--n_fireflies'     , type = int  , default = 10        , help = 'number of fireflies')
    argp.add_argument('-e', '--dist_penal_coef' , type = float, default = 0.1       , help = 'distance penalization coeficient')
    argp.add_argument('-s', '--seed'            , type = int  , default = 853295828 , help = 'seed value (Randomly determined if not specified)')
    argp.add_argument('-av', '--alpha_ver'       , type = int  , default =1   , help = 'alpha version')
    argp.add_argument(      '--verbose' ,                 action="store_true"       , help='Whether to output details for debugging')
    args = argp.parse_args()

    if args.seed == None:
        args.seed = random.randrange(2 ** 32 - 1)
        
    random.seed(args.seed)
    print('seed: {}'.format(args.seed))

    best_firefly = fireflyAlgorithm(0, args)
    print('best_firefly\'s luminosity: {}'.format(best_firefly.luminosity))

