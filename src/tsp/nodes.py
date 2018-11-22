class Nodes:

    def __init__(self, *, coords, func_distance):
        self.coords = coords
        self.names = list(coords)
        self.func_distance = func_distance
        self.length = len(coords)
        self.indexes = list(range(self.length))

    def distance(self, perm : list):

        sum_distance = 0
        for i in range(len(perm)-1):
            sum_distance += self.func_distance(self.coords[perm[i]], self.coords[perm[i+1]])
        
        return sum_distance


