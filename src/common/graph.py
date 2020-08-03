import itertools
import functools
import random
from typing import Generic, Any, Dict, Tuple, List, Set, Iterable, Iterator, Optional, Callable

import more_itertools

Node = Generic('Node')
Dist = Generic('Dist')
NodeKey = int

class Graph(Generic[Node, Dist]):

    def __init__(self,
        nodes:List[Node],
        dist_func:Callable[[Node, Node], Dist],
        is_near  :Callable[[Dist, Dist], bool] = lambda d1, d2: d1 < d2,
        *,
        allow_same_dist:Optional[bool]=True
    ):
        self.node_set = set(nodes)
        self.key_to_node = {i:node for i, node in enumerate(nodes, 1)}
        self.node_to_key = {node:i for i, node in self.key_to_node.items()}
        self.dist_func = dist_func
        self.dist_dict = {(node1, node2):dist_func(node1, node2) for node1, node2 in itertools.permutations(self.node_set, r=2)}
        self.has_same_dists = len(set(self.dist_dict.values) != len(self.dist_dict))
        if not allow_same_dist and self.has_same_dists:
            raise RuntimeError('Same distances are not allowed.')
        self.is_near = is_near


    def dist(self, node1:Node, node2:Node) -> Dist:
        return self.dist_dict[(node1, node2)]


    def total_dist(self, nodes:Iterable[Node]) -> Dist:
        return sum(self.dist(node1, node2) for node1, node2 in more_itertools.pairwise(node1))


    def total_cycle_dist(self, nodes:Iterable[Node]) -> Dist:
        first_itr, nodes = more_itertools.spy(nodes)
        return self.total_dist((*first_itr, *nodes))


    def node_keys(self) -> Iterable[NodeKey]:
        return self.key_to_node.keys()


    def encode_node_key(self, node:Node) -> NodeKey:
        return self.node_to_key[node]


    def encode_node_keys(self, nodes:Iterable[Node]) -> Iterator[NodeKey]:
        return (self.encode_node_key(node) for node in nodes)


    def decode_node_key(self, key:NodeKey) -> Node:
        return self.key_to_node[key]


    def decode_node_keys(self, keys:Iterable[NodeKey]) -> Iterator[Node]:
        return (self.decode_node_key(key) for key in keys)


    def includes(self, node_set:Set[Node]) -> bool:
        return bool(len(node_set.difference(self.node_set)))

    
    def nearest_and_its_dist(self, target_node:Node, node_set:Optional[Set[Node]]=None) -> Tuple[Node, Dist]:
        if node_set is None: node_set = self.node_set

        if not self.has_same_dists:
            return min(node_set, key=functools.cmp_to_key(
                lambda node1, node2: self.is_near(self.dist(target_node, node1), self.dist(target_node, node2))
            ))
        
        node_dists = {node: self.dist(target_node, node) for node in node_set}
        min_dist = min(node_dists.values(), key=functools.cmp_to_key(lambda dist1, dist2: self.is_near(dist1, dist2)))
        min_nodes = [node for node in node_set if node_dists[node] == min_dist]
        min_node = min_nodes[0] if len(min_nodes) == 1 else random.choice(min_nodes)

        return min_node, min_dist


    def nearest(self, target_node:Node, node_set:Optional[Set[Node]]=None) -> Node:
        return self.nearest_and_its_dist(target_node, node_set)[0]
