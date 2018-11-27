class Nodes:

    def __init__(self, *, coords, func_distance):
        self.coords = coords
        self.names = list(coords)
        self.func_distance = func_distance
        self.length = len(coords)
        self.indexes = list(range(self.length))
        

        # Calc distances between combinations of two coords

        self.distof = dict()
        for node1, coord1 in coords.items():
            self.distof[node1] = dict()
            for node2, coord2 in coords.items():
                self.distof[node1][node2] = func_distance(coord1, coord2)



    def distance(self, perm : list):

        sum_distance = 0
        for i in range(len(perm)-1):
        #    sum_distance += self.func_distance(self.coords[perm[i]], self.coords[perm[i+1]])
            sum_distance += self.distof[perm[i]][perm[i+1]]

        return sum_distance




