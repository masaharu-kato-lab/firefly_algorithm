import itertools
import numpy as np
import copy
from typing import Any, List, Dict, Tuple
Node = Tuple[int, int]

import nd_equation

class Builder:

    Method = Any
    
    def __init__(self, *,
        methods_func_dof:Dict[Method, Tuple[callable, int]], # dict(method, tuple(method lambda, degree of freedom)) 
        clusters_nodes:List[List[Node]]
    ):
        self.clusters_nodes  = clusters_nodes
        self.dof_of_methods  = {name:func_dof[1] for name, func_dof in methods_func_dof.items()}
        self.func_of_methods = {name:func_dof[0] for name, func_dof in methods_func_dof.items()}

        self.methods = methods_func_dof.keys()
        self.n_cluster = len(clusters_nodes)


    def build_with_dof(self, total_number:int) -> List[List[Node]]:
        return self.build_with_multiple_pattern(self.calc_number_of_pattern(total_number))


    def build_with_multiple_pattern(self, number_of_pattern:Dict[Method, int]) -> List[List[Node]]:
        nodes_list = []
        for pattern, number in number_of_pattern.items():
            for _ in range(number):
                nodes_list.append(self.build_with_pattern(pattern))
        return nodes_list


    def build_with_pattern(self, pattern:List[Method]) -> List[Node]:
        whole_nodes = []
        for i, nodes in enumerate(self.clusters_nodes):
            whole_nodes.extend((self.func_of_methods[pattern[i]])(nodes))
        return whole_nodes


    # dof = degree of freedom (= number of random constructing)
    def calc_number_of_pattern(self, total_number:int) -> Dict[Method, int]:

        dof_count = {}
        dof_of_patterns = {}

        # count each dof
        for pattern in itertools.product(self.methods, repeat = self.n_cluster):
            dof = sum([self.dof_of_methods[method] for method in pattern])
            dof_of_patterns[pattern] = dof
            if dof in dof_count:
                dof_count[dof] += 1
            else:
                dof_count[dof] = 1

        # convert list from dict
        l_dof_count = [0] * (max(dof_count.keys()) + 1)
        for dof, count in dof_count.items(): l_dof_count[dof] = count
        
        # transpose right side to constant of left side on equation
        l_dof_count[0] -= total_number

        # solve equation
        unit_val = nd_equation.solve(coefs = l_dof_count, prec = 0.00001, init = 1)

        # calc number (popluation) of each patterns
        number_of_patterns = {}
        for pattern, dof in dof_of_patterns.items():
            number_of_patterns[pattern] = round(unit_val ** dof)

        # adjust total number
        c_total_number = sum(number_of_patterns.values())
        if c_total_number != total_number:
            # print('total number adjustment ({} to {})'.format(c_total_number, total_number))
            max_number_pattern = max(number_of_patterns, key=number_of_patterns.get)
            number_of_patterns[max_number_pattern] += total_number - c_total_number

        # check
        if not (sum(number_of_patterns.values()) == total_number and all(number >= 1 for number in number_of_patterns.values())):
            raise RuntimeError('Invalid number of patterns.')


        return number_of_patterns



# def build_single_with_nearest_neighbor(clusters_nodes:List[List[Node]], dist_func:callable, nn_n_random:int = 1) -> List[Node]:
#     ordered_nodes = []
#     for nodes in clusters_nodes:
#         ordered_nodes.extend(build_by_nearest_neighbor(nodes, dist_func, nn_n_random))
#     return ordered_nodes


def build_with_nearest_neighbor(nodes:List[Node], dist:callable, nn_n_random:int = 1) -> List[Node]:

    ordered_nodes = []
    remain_nodes = copy.copy(nodes)
    last_node = None

    for i_itr in range(len(nodes)):

        if i_itr < nn_n_random:
            min_id = np.random.choice(range(len(remain_nodes)))
        else:
            min_id = np.argmin([dist(last_node, node) for node in remain_nodes])
        
        last_node = remain_nodes[min_id]
        ordered_nodes.append(last_node)
        remain_nodes.pop(min_id)

    return ordered_nodes


def build_randomly(nodes:List[Node]) -> List[Node]:
    return [nodes[i] for i in np.random.permutation(len(nodes))]

