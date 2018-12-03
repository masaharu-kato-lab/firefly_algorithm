import random
import math
import distance
import copy
import argparse
import time
import pickle
import map_converter # Using inside mapper.pickle

with open("res/mapper.pickle", "rb") as f:
    mapper = pickle.load(f)

# Firefly class
class Firefly:
    def __init__(self, _coords, eta, n_drones):
        self.eta = eta
        self.n_drones = n_drones

        coords = copy.copy(_coords)
        random.shuffle(coords)
        self.update(coords)

    # Update fireflies data
    def update(self, coords):
        uncertainty, distance, solution = self.evaluate(coords)
        self.x = solution
        self.uncertainty = uncertainty
        self.distance = distance
        self.luminosity = 10000 * uncertainty + self.eta * distance

    # Build the paths from a list of points
    def evaluate(self, _coords):
        coords = copy.copy(_coords)
        limit = 0
        battery = 0
        last_position = [mapper.starting_point[i] for i in range(self.n_drones)]
        start = copy.copy(last_position)
        point_time = {}
        drone_elapsed_time = [0] * self.n_drones
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
                if d >= self.n_drones:
                    d = 0

        for d in range(self.n_drones):
            if last_position[d] != start[d]:
                solution.append(way)
                path = mapper.paths[(last_position[d], start[d])][1]
                battery += limit + path
                drone_elapsed_time[d] += path * 0.5

        end_patrol_time = max(drone_elapsed_time)
        mean = []

        for element in list(point_time.values()):
            mean.append(1 - math.exp(-0.001279214 * (end_patrol_time - element)))

        uncertainty = sum(mean) / len(mean)

        return uncertainty, battery, solution


# Beta step: exploitation
def betaStep(_A, _B, gamma): #move b to a

    A = copy.copy(_A)
    B = copy.copy(_B)
    C = [None] * len(A)
    remains = copy.copy(A)
    remain_indexes = list(range(len(A)))
    visited = {i:False for i in A}

    for i, (a, b, c) in enumerate(A, B, C):
        if a == b:
            c = a
            visited[a] = True
            remains.remove(a)
            remain_indexes.remove(i)


    beta = 1 / (1 + gamma * distance.hamming(A, B))

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
def alphaStep(A, alpha):
    for _ in range(alpha):
        i1 = random.randint(0, len(A)-1)
        i2 = random.randint(0, len(A)-1)
        A[i1], A[i2] = A[i2], A[i1]

    return A


# Firefly algorithm
def fireflyAlgorithm(z, args):

    if args.verbose: print(args)

    points = [(32, 1122), (271, 1067), (209, 993), (184, 1205), (303, 1220), (400, 1122), (505, 1214), (669, 1202), (779, 1026), (912, 1029), (1483, 1156), (1614, 991), (1576, 567), (1502, 395), (1618, 227), (1448, 634), (967, 690), (1059, 842), (759, 823), (1387, 174), (1073, 82), (944, 327), (866, 512), (748, 638), (487, 896), (118, 653), (35, 902), (502, 339), (683, 316), (694, 123), (45, 52), (367, 39)]
    swarm = [Firefly(points, args.dist_penal_coef, args.n_drones) for i in range(args.n_fireflies)]
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
                        c = alphaStep([elm for sub in swarm[i].x for elm in sub], args.alpha)
                        swarm[i].update(c)

        swarm = sorted(swarm, key = lambda ff: ff.luminosity)
        if swarm[0].luminosity == swarm[-1].luminosity: #If all the fireflies are at the same position

        # if all([s.luminosity == swarm[0].luminosity for s in swarm[1:]]): #all fireflies are at the same position
            if args.verbose: print("*** swarm blocked ***")

            for i in range(1, len(swarm)):
                c = alphaStep([elm for sub in swarm[i].x for elm in sub], args.alpha)
                swarm[i].update(c)
                
            swarm = sorted(swarm, key = lambda ff: ff.luminosity)

        if best_firefly.luminosity > swarm[0].luminosity:
            best_firefly = copy.deepcopy(swarm[0])
            
        if args.verbose and t % 100 == 0:
            print("Iteration: {}\nSwarm: {}, Best firefly: {}\n", t, [s.luminosity for s in swarm], best_firefly.luminosity)

        t += 1

    endTime = time.time()

    if args.verbose:
        print("Elapsed time: ", endTime - start_time)

    return best_firefly



if __name__ == "__main__":
    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--n_drones'        , type = int  , default = 2     , help = 'number of drones')
    parser.add_argument('-i', '--n_iteration'     , type = int  , default = 3000  , help = 'number of iterations')
    parser.add_argument('-g', '--gamma'           , type = float, default = 0.90  , help = 'firefly algorithm gamma')
    parser.add_argument('-a', '--alpha'           , type = int  , default = 1     , help = 'firefly algorithm alpha')
    parser.add_argument('-f', '--n_fireflies'     , type = int  , default = 10    , help = 'number of fireflies')
    parser.add_argument('-e', '--dist_penal_coef' , type = float, default = 0.1   , help = 'distance penalization coeficient')
    parser.add_argument('-p', '--verbose'         , type = int  , default = False , help = 'enable/desable verbose')
    parser.add_argument('-s', '--seed'            , type = int  , default = 853295828 , help = 'seed value (Randomly determined if not specified)')
    args = parser.parse_args()

    if args.seed == None:
        args.seed = random.randrange(2 ** 32 - 1)
        
    random.seed(args.seed)
    print('seed: {}'.format(args.seed))

    best_firefly = fireflyAlgorithm(0, args)
    print('best_firefly\'s luminosity: {}'.format(best_firefly.luminosity))

