import numpy as np

cpcoords = {'A':[45, 52], 'B':[192, 38], 'C':[114, 82], 'D':[241, 75], 'E':[123, 181], 'F':[399, 177], 'G':[31, 245], 'H':[162, 229], 'I':[266, 211], 'J':[254, 263], 'K':[334, 245]}
nodes = list(cpcoords.values())
dist = lambda n1, n2: np.linalg.norm(n1, n2)
start_node = [210, 130]


def nodes_of_str(cps:str):
    return {cpcoords[cpname] for cpname in cps}

