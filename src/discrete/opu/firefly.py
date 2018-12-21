import copy
import math
import random
import pickle

class Luminosity:

    def __init__(self, *,
        coords        : dict,  # dict of coordinate with node as key
        n_drones      : int,   # number of available drone(s)
        u_weight      : float, # weight of uncertainly (compare with distance) (Real number between 0.0 and 1.0)
        min_distance  : float, # Assumed minimum distance
        max_distance  : float, # Assumed maximum distance
        battery_dist  : float = 3000, # Max movable distance by one battery
        drone_speed   : float = 2.0 , # Speed of drone
    ):
        self.coords = copy.copy(coords)      
        self.n_drones = n_drones    
        self.u_weight = u_weight    
        self.battery_dist = battery_dist
        self.drone_speed = drone_speed
        self.min_distance = min_distance
        self.max_distance = max_distance

        with open("res/mapper.pickle", "rb") as f:
            self.mapper = pickle.load(f)

        for i in range(self.n_drones):
            self.coords['drone'+str(i)] = self.mapper.starting_point[i] 


        # self.cache_luminosity = {}


    # calc distance between two nodes
    def dist_of_2(self, node1, node2):
        return self.mapper.paths[(self.coords[node1], self.coords[node2])][1]


    # calc elasped time from distance drone moved
    def time_by_dist(self, dist):
        return dist / self.drone_speed


    # normalize distance
    def normalize_distance(self, dist):
        return (dist - self.min_distance) / (self.max_distance - self.min_distance)


    # # get luminosity of permutation with cache
    # def luminosity(self, perm:tuple):

    #     if perm not in self.cache_luminosity:
    #         self.cache_luminosity[perm] = self.calc_luminosity(perm)
        
    #     return self.cache_luminosity[perm]
    
    

    # Build the paths from a list of points
    def luminosity(self, perm:tuple):

        remain_nodes = list(perm)
        current_dist = 0
        whole_distance = 0
        last_node = ['drone'+str(i) for i in range(self.n_drones)]
        start_node = copy.copy(last_node)
        nodes_last_visited_time = {}
        drone_elapsed_time = [0] * self.n_drones
        d = 0

        while len(remain_nodes):
            
            target_node = remain_nodes[0]

            if current_dist + self.dist_of_2(last_node[d], target_node) + self.dist_of_2(target_node, start_node[d]) < self.battery_dist:
                
                additional_dist = self.dist_of_2(last_node[d], target_node)
                current_dist += additional_dist
                drone_elapsed_time[d] += self.time_by_dist(additional_dist)

                nodes_last_visited_time[target_node] = drone_elapsed_time[d]
                last_node[d] = remain_nodes.pop(0)


            else:
                additional_dist = self.dist_of_2(last_node[d], start_node[d])
                whole_distance += current_dist + additional_dist
                drone_elapsed_time[d] += self.time_by_dist(additional_dist)

                d += 1
                if d >= self.n_drones:
                    d = 0

                current_dist = 0
                last_node[d] = start_node[d]
                

        for d in range(self.n_drones):

            if last_node[d] != start_node[d]:

                additional_dist = self.dist_of_2(last_node[d], start_node[d])
                whole_distance += current_dist + additional_dist
                drone_elapsed_time[d] += self.time_by_dist(additional_dist)


        uncertainty = self.calc_uncertainty(nodes_last_visited_time, max(drone_elapsed_time))
        luminosity = self.u_weight * uncertainty + (1.0 - self.u_weight) * self.normalize_distance(whole_distance)

        return luminosity


    def calc_uncertainty(self, nodes_last_visited_time, end_patrol_time):
        
        mean = []
        for node_last_visited_time in list(nodes_last_visited_time.values()):
            mean.append(1 - math.exp(-0.001279214 * (end_patrol_time - node_last_visited_time)))

        return sum(mean) / len(mean)


    # Calc distance of coords
    def distance(self, perm:tuple):

        distance = 0
        for i in range(len(perm)-1):
            distance += self.dist_of_2(perm[i], perm[i+1])

        return distance


