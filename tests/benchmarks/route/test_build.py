from src.route_planner import generate
from src.common import permutation
import field_for_test as fl


def test_build_greedy():
    ans = build.PatternedPermutation(fl.nodes_of_str('DBCAEHJIKFG'), 'G')

    for _ in range(10):
        assert ans == build.build_greedy(fl.nodes, fl.dist, start_node=fl.start_node)


def test_build_randomly():
    for _ in range(10):
        ret = build.build_randomly(fl.nodes)
        assert permutation.is_valid(ret.nodes, fl.nodes) and ret.pattern == 'R'
