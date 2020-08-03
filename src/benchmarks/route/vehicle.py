import copy
import math
import pickle
import sys
from functools import total_ordering

# from types import List, Dict, Tuple, Node

from typing import Any, List, Dict, Tuple, Generic, TypeVar
Pos = TypeVar('Pos', Any)
Time = float


# 代わりに Graph を使う
# class Field(Generic[Pos]):

#     def __init__(self, filepath : str):

#         self.node_ = nodes
#         self.node_set = set(self.nodes)
#         self.home_poses = mapper.starting_point
#         self.distance_of = {node_pair:path[1] for node_pair, path in mapper.paths.items()}

#         self.nodes_to_index:Dict[Node, int] = {}
#         for i, node in enumerate(self.nodes):
#             self.nodes_to_index[node] = i + 1


#     # Calc distance of two points
#     def distance(self, c1:Node, c2:Node) -> float:
#         if c1 == c2: return 0.0
#         return self.distance_of[(c1, c2)]


#     # Calc distance of coords
#     def distance_of_nodes(self, nodes:List[Node]) -> float:

#         distance = 0.0
#         for i in range(len(nodes)-1):
#             distance += self.distance(nodes[i], nodes[i+1])

#         return distance


@dataclass
class VehicleProperty(Generic[Pos]):
    field                : Field[Pos]
    home_pos             : Pos
    speed                : float # = 0.5
    battery_capacity     : float # = 3000.0
    battery_per_distance : float # = 1.0



class Vehicle(Generic[Pos]):

    def __init__(self, props:VehicleProperty[Pos]):
        self.props = props

        self.pos_history = [self.props.home_pos]
        self.last_pos = self.props.home_pos
        self.total_distance = 0.0
        self.elapsed_time = 0.0
        self.battery_remain = self.props.battery_capacity


    def _distance(self, c1:Pos, c2:Pos) -> float:
        return self.props.pathdata.distance(c1, c2)


    def move_to(self, target:Pos) -> None:
        if self.last_pos == target: return

        c_distance = self._distance(self.last_pos, target)

        self.pos_history.append(target)
        self.last_pos = target

        self.total_distance += c_distance
        self.elapsed_time += c_distance * self.props.speed

        self.battery_remain -= c_distance * self.props.battery_per_distance
        if self.battery_remain < 0:
            raise RuntimeError('Out of battery.')

        if self.last_pos == self.props.home_pos:
            self.battery_remain = self.props.battery_capacity


    def try_move_to(self, target:Pos) -> bool:

        if self._distance(self.last_pos, target) + self._distance(target, self.props.home_pos) > self.battery_remain:
            return False

        self.move_to(target)
        return True


    def return_home(self) -> None:
        self.move_to(self.props.home_pos)


class PlanGenerator:

    def __init__(self, *,
        field:Field,
        vehicle_prop:VehicleProperty,
        n_drones:int,
        safety_weight:float, # weight of uncertainly
        distance_weight:float, # weight of distance
    ):
        self.field = field
        self.vehicle_prop = vehicle_prop
        self.n_drones = n_drones
        self.safety_weight = safety_weight
        self.distance_weight = distance_weight


    def make(self, clusters_nodes):
        return Plan(self, clusters_nodes)


@total_ordering
class Plan:

    def __init__(self, props:PlanGenerator, clusters_nodes:List[List[Node]]):
        self.clusters_nodes = clusters_nodes
        self.vehicles = [Vehicle(props.vehicle_prop) for _ in range(props.n_drones)]

        nodes_to_index = props.vehicle_prop.pathdata.nodes_to_index

        last_visit_time_on_nodes = {}
        i_drone = 0
        text = ''

        for nodes in self.clusters_nodes:
            
            text += '['
            remain_nodes = copy.copy(nodes)

            while len(remain_nodes):
                vehicle = self.vehicles[i_drone]
                text += '|{}>'.format(i_drone)

                while len(remain_nodes):
                    node = remain_nodes[0]
                    if not vehicle.try_move_to(node): break
                    last_visit_time_on_nodes[node] = vehicle.elapsed_time
                    text += '{:>2} '.format(nodes_to_index[node])
                    remain_nodes.pop(0)
                        
                vehicle.return_home()
                i_drone = (i_drone + 1) % props.n_drones

            text += ']'



        self.total_distance = sum([vehicle.total_distance for vehicle in self.vehicles])
        self.whole_time = max([vehicle.elapsed_time   for vehicle in self.vehicles])
        safety_on_nodes = [math.exp(-0.001279214 * (self.whole_time - last_visit_time)) for last_visit_time in last_visit_time_on_nodes.values()]
        self.average_safety = sum(safety_on_nodes) / len(safety_on_nodes)

    #   normalized_distance = ((sum_distance - distance_range.start) / (distance_range.stop - distance_range.start))
        self.value = props.safety_weight * (1.0 - self.average_safety) + props.distance_weight * self.total_distance
        self.text = text


    def __lt__(self, plan):
        if not isinstance(plan, Plan): return NotImplemented
        return self.value < plan.value


    def __eq__(self, plan):
        if not isinstance(plan, Plan): return NotImplemented
        return self.value == plan.value



