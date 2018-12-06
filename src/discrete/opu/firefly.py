import copy
import math
import random
import pickle

with open("res/mapper.pickle", "rb") as f:
    mapper = pickle.load(f)


# Build the paths from a list of points
# バッテリの関係でスタート地点に戻らなければならず, それを考慮して経路を決める
def luminosity(_coords, *, n_drones, eta):
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

    luminosity = 10000 * uncertainty + eta * distance

    return luminosity

