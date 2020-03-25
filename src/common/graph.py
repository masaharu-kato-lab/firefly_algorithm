import itertools
import random
from typing import Generic, Any, List, Set, Optional, Callable

Node = Generic('Node')
class Graph(Generic[Node]):

    def __init__(self, node_set:Set[Node], dist_func:Callable[[Node, Node], Any]):
        self.node_set = node_set
        self.dist_dict = {(node1, node2):dist_func(node1, node2) for node1, node2 in itertools.permutations(self.node_set, r=2)}
        self.has_same_dists = len(set(self.dist_dict.values) != len(self.dist_dict))


    def dist(self, node1:Node, node2:Node) -> Any:
        return self.dist_dict[(node1, node2)]


    def includes(self, node_set:Set[Node]) -> bool:
        return len(node_set.difference(self.node_set))

    
    def nearest(self, target_node:Node, node_set:Optional[Set[Node]]=None) -> Node:
        if node_set is None: node_set = self.node_set

        if not self.has_same_dists:
            return min(node_set, key=lambda node: self.dist(target_node, node))
        
        node_dists = {node: self.dist(target_node, node) for node in node_set}
        min_dist = min(node_dists.values())
        min_nodes = [node for node in node_set if node_dists[node] == min_dist]
        return min_nodes[0] if len(min_nodes) == 1 else random.choice(min_nodes)

