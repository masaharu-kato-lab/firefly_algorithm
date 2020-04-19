import random
from common.graph import Graph

from typing import Any, Callable, Optional, List, Set, Generic
Node = Generic('Node', Any)


def greedy(graph:Graph[Node], node_set:Set[Node]=None, init_node:Optional[Node]=None, n_random:int=0) -> List[Node]:

    remains = graph.node_set.copy() if node_set is None else node_set
    ret = random.sample(remains, n_random)

    last = init_node
    while(remains):
        last = graph.nearest(last, remains)
        ret.append(last)
        remains.pop(last)

    return ret


def randomly(node_set:Set[Node], n:Optional[int]=None) -> List[Node]:
    return random.sample(node_set, len(node_set) if n is None else n)
