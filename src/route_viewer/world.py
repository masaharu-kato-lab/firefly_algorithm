import pickle
import matplotlib as mpl #type:ignore
import matplotlib.pyplot as plt #type:ignore
import sys
import os

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

class World:

    def __init__(self, mapper_path:str):

        with open(mapper_path, mode='rb') as f:
            mapper = pickle.load(f)

        self.world = mapper.world
        self.nodes = mapper.default_targets
        self.depot_pos = mapper.starting_point[0]

        

    def plot_world(self, *, color = 'black', bgcolor = 'white'):
        plt.imshow(
            self.world,
            interpolation="none",
            cmap=mpl.colors.ListedColormap([bgcolor, color, 'red', 'orange'])
        )


    def plot_nodes(self, **options):
        plt.scatter(
            [p[0] for p in self.nodes],
            [p[1] for p in self.nodes],
            **options
        )


    def plot_depot(self, **options):
        plt.scatter(
            self.depot_pos[0],
            self.depot_pos[1],
            **options
        )
