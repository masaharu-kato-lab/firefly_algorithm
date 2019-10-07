import copy
import math
import random
import pickle


class Drone:

    def __init__(self):
        self.path_data = None
        self.home_pos = None
        self.speed = 0.5
        self.battery_capacity = 3000
        self.battery_per_distance = 1.0

        self.pos_list = []
        self.last_pos = None
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


    def try_move_to(self, target):

        if self.distance(self.last_pos, target) + self.distance(target, self.home_pos) > self.battery_remain:
            return False

        self._move_to(target)
        return True


    def return_home(self):
        self._move_to(self.home_pos)



class PathDecoder:

    def __init__(
        self,
        nodes_list   : list,  # list of coordinates on target permutation
        *,
        n_drones     : int,   # number of available drone(s)
    ):
        self.last_visit_time = {}
        self.n_drones = n_drones
     #   self.remain_nodes = copy.copy(coords)


    def make_one_round(self, remain_nodes : list, drone : Drone):

        while len(remain_nodes):
            node = remain_nodes[0]
            
            if drone.try_move_to(node):
                self.last_visit_time[node] = drone.elapsed_time
                remain_nodes.pop(0)

            else:
                break

        drone.return_home()


    # Build the paths from a list of points
    # TODO: 実装
    def build(self):

        drones = [Drone() for _ in range(self.n_drones)]
        i_drone = 0
        c_drone = drones[i_drone]

        remain_nodes = []

        self.make_one_round(remain_nodes, c_drone)


def calc_evaluation_value(self,
    *,
    drones : list,
    last_visit_time_on_nodes : dict,
    safety_weight : float, # weight of uncertainly (compare with distance) (Real number between 0.0 and 1.0)
    min_distance : float, # Assumed minimum distance
    max_distance : float, # Assumed maximum distance
):

    sum_distance    = sum([drone.total_distance for drone in drones])
    end_patrol_time = max([drone.elasped_time   for drone in drones])
    safety_on_nodes = [math.exp(-0.001279214 * (end_patrol_time - last_visit_time)) for last_visit_time in last_visit_time_on_nodes.values()]
    average_safety = sum(safety_on_nodes) / len(safety_on_nodes)

    normalized_distance = ((sum_distance - min_distance) / (max_distance - min_distance))
    luminosity = safety_weight * (1.0 - average_safety) + (1.0 - safety_weight) * normalized_distance

    return luminosity



class PathData:
    
    def __init__(self, filepath : str):
        with open(filepath, "rb") as f:
            self.mapper = pickle.load(f)

        self.nodes = self.mapper.default_targets


    # Calc distance of two points
    def distance(self, c1 : tuple, c2 : tuple):

        return self.mapper.paths[(c1, c2)][1]


    # Calc distance of coords
    def distance_of_nodes(self, nodes : list):

        distance = 0
        for i in range(len(nodes)-1):
            distance += self.distance(nodes[i], nodes[i+1])

        return distance

