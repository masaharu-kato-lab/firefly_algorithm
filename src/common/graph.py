import itertools
import functools
import random
from typing import Generic, Any, Dict, Tuple, List, Set, Optional, Callable

Node = Generic('Node')
Dist = Generic('Dist')
class Graph(Generic[Node, Dist]):

    def __init__(self,
        node_set:Set[Node],
        dist_func:Callable[[Node, Node], Dist],
        is_near  :Callable[[Dist, Dist], bool],
        *,
        allow_same_dist:Optional[bool]=True
    ):
        self.node_set = node_set
        self.dist_func = dist_func
        self.dist_dict = {(node1, node2):dist_func(node1, node2) for node1, node2 in itertools.permutations(self.node_set, r=2)}
        self.has_same_dists = len(set(self.dist_dict.values) != len(self.dist_dict))
        if not allow_same_dist and self.has_same_dists:
            raise RuntimeError('Same distances are not allowed.')
        self.is_near = is_near


    def dist(self, node1:Node, node2:Node) -> Dist:
        return self.dist_dict[(node1, node2)]


    def includes(self, node_set:Set[Node]) -> bool:
        return len(node_set.difference(self.node_set))

    
    def nearest(self, target_node:Node, node_set:Optional[Set[Node]]=None) -> Node:
        if node_set is None: node_set = self.node_set

        if not self.has_same_dists:
            return min(node_set, key=functools.cmp_to_key(
                lambda node1, node2: self.is_near(self.dist(target_node, node1), self.dist(target_node, node2))
            ))
        
        node_dists = {node: self.dist(target_node, node) for node in node_set}
        min_dist = min(node_dists.values(), key=functools.cmp_to_key(lambda dist1, dist2: self.is_near(dist1, dist2)))
        min_nodes = [node for node in node_set if node_dists[node] == min_dist]
        return min_nodes[0] if len(min_nodes) == 1 else random.choice(min_nodes)
