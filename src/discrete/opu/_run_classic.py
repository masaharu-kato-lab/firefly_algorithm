import random
import math
import distance
import copy
import argparse
import time
import pickle


with open("res/mapper.pickle", "rb") as f:
    mapper = pickle.load(f)

# Firefly class
class Firefly:
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


# Beta step: exploitation
def betaStep(a, b, gamma): #move b to a

    A = [element for subList in a for element in subList]
    B = [element for subList in b for element in subList]
    d = distance.hamming(A, B)
    beta = 1 / (1 + gamma * d)
    c = ['' for i in A]
    to_insert = [i for i in A]
    idx_rand=[i for i in range(len(A))]
    visited_dic={i:False for i in A}

    for idx in range(len(idx_rand)):
        if A[idx] == B[idx]:
            c[idx] = A[idx]
            visited_dic[A[idx]] = True
            to_insert.remove(A[idx])
            idx_rand.remove(idx)

    for idx in idx_rand:
        if random.random() < beta:
            if not visited_dic[A[idx]]:
                c[idx] = A[idx]
                to_insert.remove(A[idx])
                visited_dic[A[idx]] = True

            elif not visited_dic[B[idx]]:
                c[idx] = B[idx]
                to_insert.remove(B[idx])
                visited_dic[B[idx]] = True

        else:
            if not visited_dic[B[idx]]:
                c[idx] = B[idx]
                to_insert.remove(B[idx])
                visited_dic[B[idx]] = True

            elif not visited_dic[A[idx]]:
                c[idx] = A[idx]
                to_insert.remove(A[idx])
                visited_dic[A[idx]] = True


    random.shuffle(to_insert)


    for insert in to_insert:
        idx = c.index('')
        c[idx] = insert

    return c



# Alpha step: exploration (v1)
def alphaStep1(a, alpha):
    for _ in range(alpha):
        x = random.randint(0, len(a)-1)
        y = random.randint(0, len(a)-1)
        a[x], a[y] = a[y], a[x]
    return a


# Firefly algorithm
def fireflyAlgorithm(z, args):

    if args.verbose: print(args)

    points = [(32, 1122), (271, 1067), (209, 993), (184, 1205), (303, 1220), (400, 1122), (505, 1214), (669, 1202), (779, 1026), (912, 1029), (1483, 1156), (1614, 991), (1576, 567), (1502, 395), (1618, 227), (1448, 634), (967, 690), (1059, 842), (759, 823), (1387, 174), (1073, 82), (944, 327), (866, 512), (748, 638), (487, 896), (118, 653), (35, 902), (502, 339), (683, 316), (694, 123), (45, 52), (367, 39)]
    swarm = [Firefly(points, args.dist_penal_coef, args.n_drones) for i in range(args.n_fireflies)]
    swarm = sorted(swarm, key = lambda ff: ff.luminosity)
    bestFirefly = copy.deepcopy(swarm[0])


    if args.verbose: print("Best firefly init: ", bestFirefly.luminosity)

    tab = ([0], [bestFirefly.luminosity])
    t = 0
    n = len(swarm)
    startTime = time.time()

    while t < args.n_iteration:
        for i in range(n):
            for j in range(n):
                if j != i:
                    if swarm[j].luminosity < swarm[i].luminosity:
                        # c = betaStep(swarm[j].x, swarm[i].x, args.gamma)
                        c = [element for subList in swarm[i].x for element in subList]
                        c = alphaStep1(c, args.alpha)
                        swarm[i].update(c)

        swarm = sorted(swarm, key = lambda ff: ff.luminosity)
        if swarm[0].luminosity == swarm[-1].luminosity: #If all the fireflies are at the same position

        # if all([s.luminosity == swarm[0].luminosity for s in swarm[1:]]): #all fireflies are at the same position
            if args.verbose: print("*** swarm blocked ***")

            for i in range(1, len(swarm)):
                c = [element for subList in swarm[i].x for element in subList]
                c = alphaStep1(c, args.alpha)
                swarm[i].update(c)
            swarm = sorted(swarm, key = lambda ff: ff.luminosity)

        if bestFirefly.luminosity > swarm[0].luminosity:
            bestFirefly = copy.deepcopy(swarm[0])
            
        if t % 100 == 0:
            if args.verbose:
                print("")
                print("Iteration: ", t)
                print("Swarm: ", [s.luminosity for s in swarm])
                print("Best firefly: ", bestFirefly.luminosity)

            tab[0].append(t+1)
            tab[1].append(bestFirefly.luminosity)
        t += 1
    endTime = time.time()

    if args.verbose: print("Elapsed time: ", endTime - startTime)

    return bestFirefly



if __name__ == "__main__":
    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d"  , '--n_drones'        , type = int  , default = 2    , help = "number of drones")
    parser.add_argument("-i"  , '--n_iteration'     , type = int  , default = 1000 , help = "number of iterations")
    parser.add_argument("-g"  , '--gamma'           , type = float, default = 0.90 , help = "firefly algorithm gamma")
    parser.add_argument("-a"  , '--alpha'           , type = int  , default = 1    , help = "firefly algorithm alpha")
    parser.add_argument("-f"  , '--n_fireflies'     , type = int  , default = 10   , help = "number of fireflies")
    parser.add_argument("-e"  , '--dist_penal_coef' , type = float, default = 0.1  , help = "distance penalization coeficient")
    parser.add_argument("-p"  , '--verbose'         , type = int  , default = 1    , help = "enable/desable verbose")
    args = parser.parse_args()

    bestFirefly = fireflyAlgorithm(0, args)

