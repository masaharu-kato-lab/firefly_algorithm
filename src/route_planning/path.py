import copy
import math
import random
import pickle


class Drone:

    def __init__(self, path_data):
        self.path_data = path_data
        self.home_pos = path_data.home_poses[0]
        self.speed = 0.5
        self.battery_capacity = 3000
        self.battery_per_distance = 1.0

        self.pos_list = []
        self.last_pos = self.home_pos
        self.total_distance = 0
        self.elapsed_time = 0
        self.battery_remain = self.battery_capacity


    def distance(self, c1, c2):
        return self.path_data.distance(c1, c2)


    def _move_to(self, target):
        if self.last_pos == target: return

        c_distance = self.distance(self.last_pos, target)

        self.pos_list.append(target)
        self.last_pos = target

        self.total_distance += c_distance
        self.elapsed_time += c_distance * self.speed

        self.battery_remain -= c_distance * self.battery_per_distance
        if self.battery_remain < 0:
            raise RuntimeError('Out of battery.')


    def try_move_to(self, target:tuple):

        if self.distance(self.last_pos, target) + self.distance(target, self.home_pos) > self.battery_remain:
            return False

        self._move_to(target)
        return True


    def return_home(self):
        self._move_to(self.home_pos)



def calc_evaluation_value(
    clusters_nodes:list,  # list of list
    *,
    path_data, # PathData class
    n_drones:int,   # number of available drone(s)
    safety_weight:float, # weight of uncertainly (compare with distance) (Real number between 0.0 and 1.0)
    distance_range :range, # Assumed distance range
):
    drones, last_visit_time_on_nodes = build_drones_path(clusters_nodes, path_data = path_data, n_drones = n_drones)
    return calc_evaluation_value_with_drones(
        drones = drones,
        last_visit_time_on_nodes = last_visit_time_on_nodes,
        safety_weight = safety_weight,
        distance_range = distance_range
    )



# Build the paths from a list of points
def build_drones_path(
    clusters_nodes:list,  # list of list
    *,
    path_data, # PathData class
    n_drones:int   # number of available drone(s)
):

    last_visit_time_on_nodes = {}
    drones = [Drone(path_data) for _ in range(n_drones)]
    i_drone = 0

    for nodes in clusters_nodes:

        remain_nodes = copy.copy(nodes)
        drone = drones[i_drone]

        while len(remain_nodes):
            node = remain_nodes[0]
            if not drone.try_move_to(node): break
            last_visit_time_on_nodes[node] = drone.elapsed_time
            remain_nodes.pop(0)
                
        drone.return_home()
        i_drone = (i_drone + 1) % n_drones

    return drones, last_visit_time_on_nodes



def calc_evaluation_value_with_drones(*,
    drones:list, # list of Drone object
    last_visit_time_on_nodes:dict,
    safety_weight:float, # weight of uncertainly (compare with distance) (Real number between 0.0 and 1.0)
    distance_range :range, # Assumed distance range
):

    sum_distance    = sum([drone.total_distance for drone in drones])
    end_patrol_time = max([drone.elapsed_time   for drone in drones])
    safety_on_nodes = [math.exp(-0.001279214 * (end_patrol_time - last_visit_time)) for last_visit_time in last_visit_time_on_nodes.values()]
    average_safety = sum(safety_on_nodes) / len(safety_on_nodes)

    normalized_distance = ((sum_distance - distance_range.start) / (distance_range.stop - distance_range.start))
    luminosity = safety_weight * (1.0 - average_safety) + (1.0 - safety_weight) * normalized_distance

    return luminosity



class PathData:
    
    def __init__(self, filepath : str):
        with open(filepath, "rb") as f:
            self.mapper = pickle.load(f)

        self.nodes = self.mapper.default_targets
        self.home_poses = self.mapper.starting_point


    # Calc distance of two points
    def distance(self, c1:tuple, c2:tuple):
        if c1 == c2: return 0
        return self.mapper.paths[(c1, c2)][1]


    # Calc distance of coords
    def distance_of_nodes(self, nodes : list):

        distance = 0
        for i in range(len(nodes)-1):
            distance += self.distance(nodes[i], nodes[i+1])

        return distance

