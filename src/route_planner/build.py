import copy
from itertools import chain, product

import numpy as np #type:ignore

import nd_equation

from typing import Any, Callable, Dict, Iterable, List, Tuple, Union
Node = Tuple[int, int]


class PatternedPermutation:
    def __init__(self, nodes:List[Node], pattern:Union[str, tuple]):
        self.nodes = nodes
        self.pattern = pattern
        if not pattern: raise RuntimeError('Pattern is empty.')


def chain_patterned_permutations(_perms:Iterable[PatternedPermutation]):
    perms = list(_perms)
    return PatternedPermutation(
        [*chain.from_iterable(p.nodes for p in perms)],
        tuple(p.pattern for p in perms)
    )



class Builder:
    
    def __init__(self, *,
        methods_func_dof:Dict[Any, Tuple[Callable, int]], # dict(method, tuple(method lambda, degree of freedom)) 
        clusters_nodes:List[List[Node]]
    ):
        self.clusters_nodes  = clusters_nodes
        self.dof_of_methods  = {name:func_dof[1] for name, func_dof in methods_func_dof.items()}
        self.func_of_methods = {name:func_dof[0] for name, func_dof in methods_func_dof.items()}

        self.methods = methods_func_dof.keys()
        self.n_cluster = len(clusters_nodes)


    def build_with_dof(self, total_number:int) -> List[PatternedPermutation]:
        return self.build_with_multiple_pattern(self.calc_number_of_pattern(total_number))


    def build_with_multiple_pattern(self, number_of_pattern:Dict[Any, int]) -> List[PatternedPermutation]:
        return [*chain.from_iterable((self.build_with_pattern(pattern) for _ in range(number)) for pattern, number in number_of_pattern.items())]


    def build_with_pattern(self, pattern:List[Any]) -> PatternedPermutation:
        return chain_patterned_permutations(
            (self.func_of_methods[pattern[i]])(nodes)
            for i, nodes in enumerate(self.clusters_nodes)
        )


    # dof = degree of freedom (= number of random constructing)
    def calc_number_of_pattern(self, total_number:int) -> Dict[Any, int]:

        dof_count:Dict[int, int] = {}
        dof_of_patterns = {}

        # count each dof
        for pattern in product(self.methods, repeat = self.n_cluster):
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


def build_greedy(nodes:List[Node], dist:Callable, nn_n_random:int = 1) -> PatternedPermutation:

    ordered_nodes = []
    remain_nodes = copy.copy(nodes)
    last_node = None

    for i_itr in range(len(nodes)):

        if i_itr < nn_n_random:
            target_id = np.random.choice(range(len(remain_nodes)))
        else:
            dists = np.array([dist(last_node, node) for node in remain_nodes])
            min_ids = np.where(dists == dists.min())[0]
            if len(min_ids) > 1: print("choice one from multiple.")
            target_id = np.random.choice(min_ids) if len(min_ids) > 1 else min_ids[0]
        
        last_node = remain_nodes[target_id]
        ordered_nodes.append(last_node)
        remain_nodes.pop(target_id)

    if remain_nodes: raise RuntimeError('Remain nodes is not empty.')

    return PatternedPermutation(ordered_nodes, 'G')


def build_randomly(nodes:List[Node]) -> PatternedPermutation:
    return PatternedPermutation([nodes[i] for i in np.random.permutation(len(nodes))], 'R')

