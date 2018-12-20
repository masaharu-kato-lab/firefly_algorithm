import copy
import math
import random
import pickle

with open("res/mapper.pickle", "rb") as f:
    mapper = pickle.load(f)


# Build the paths from a list of points
# バッテリの関係でスタート地点に戻らなければならず, それを考慮して経路を決める
def luminosity(
    _coords      : list,  # list of coordinates on target permutation
    *,
    n_drones     : int,   # number of available drone(s)
    u_weight     : float, # weight of uncertainly (compare with distance) (Real number between 0.0 and 1.0)
    min_distance : float, # Assumed minimum distance
    max_distance : float, # Assumed maximum distance
):
    coords = copy.copy(_coords)
    limit = 0
    distance = 0
    last_position = [mapper.starting_point[i] for i in range(n_drones)]
    start = copy.copy(last_position)
    point_time = {}
    drone_elapsed_time = [0] * n_drones
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
            distance += limit + path
            limit = 0
            drone_elapsed_time[d] += path * 0.5
            last_position[d] = start[d]
            d += 1
            if d >= n_drones:
                d = 0

    for d in range(n_drones):
        if last_position[d] != start[d]:
            solution.append(way)
            path = mapper.paths[(last_position[d], start[d])][1]
            distance += limit + path
            drone_elapsed_time[d] += path * 0.5

    end_patrol_time = max(drone_elapsed_time)
    mean = []

    for element in list(point_time.values()):
        mean.append(1 - math.exp(-0.001279214 * (end_patrol_time - element)))

    uncertainty = sum(mean) / len(mean)

    # uncertainly : 0.0 ~ 1.0
    # distance : 10,000 ~ 20,000
    # 比率を0.2ずつ見ていく
    normalized_distance = ((distance - min_distance) / (max_distance - min_distance))
    luminosity = u_weight * uncertainty + (1.0 - u_weight) * normalized_distance

    return luminosity



# Calc distance of coords
def distance(coords):

    distance = 0
    for i in range(len(coords)-1):
        distance += mapper.paths[(coords[i], coords[i+1])][1]

    return distance


