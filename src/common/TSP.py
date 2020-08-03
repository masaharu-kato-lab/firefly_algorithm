from .problem import Problem
from .graph import Graph


def basic_tsp(graph:Graph, target_) -> Problem:
    return Problem(
        set(graph.node_keys()),
        lambda key_perm: graph.total_cycle_dist(graph.decode_node_keys(key_perm)),
        lambda v1, v2: v1 < v2,
    )

