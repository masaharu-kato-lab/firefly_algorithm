import copy

# check validity
def isValid(perm:list, nodes:list):

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
