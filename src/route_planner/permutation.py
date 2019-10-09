import copy
from typing import List, Tuple
Node = Tuple[int, int]

# check permutation validity
def is_valid(perm:List[Node], nodes:List[Node]) -> bool:

    nodes = copy.copy(nodes)

    for node in perm:
        # check if node is in nodes and not used yet
        if(node in nodes):
            nodes.remove(node)
        else:
            return False

    # check if there are unuse nodes
    if len(nodes):
        return False

    return True
