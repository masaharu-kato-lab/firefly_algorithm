from collections import Counter

class PathCounter:

    def __init__(self):
        self.directed_counter = Counter()
        self.undirected_counter = Counter()


    def add_path(self, path:tuple):
        self.directed_counter.update(path)
        self.undirected_counter.update(self._undirected_path(path))

    
    def add_poses(self, poses:list):
        paths = list(zip(poses[:-1], poses[1:]))
        self.directed_counter.update(paths)
        self.undirected_counter.update([self._undirected_path(path) for path in paths])


    @classmethod
    def _undirected_path(cls, path):
        (p1, p2) = path
        return (p1, p2) if cls._pos_less_than(p1, p2) else (p2, p1)

    @classmethod
    def _pos_less_than(cls, p1, p2):
        if len(p1) != len(p2): raise RuntimeError('Different dimentional positions.')
        for e1, e2 in zip(p1, p2):
            if e1 < e2: return True
            if e1 > e2: return False
        raise RuntimeError('Positions must be different.')

