import pickle
import matplotlib as mpl
import matplotlib.pyplot as plt


class World:

    def __init__(self, mapper_path:str):

        with open(mapper_path, mode='rb') as f:
            mapper = pickle.load(f)

        self.world = mapper.world

        

    def plot_world(self):
        plt.imshow(
            self.world,
            interpolation="none",
            cmap=mpl.colors.ListedColormap(['white', 'black', 'red', 'orange'])
        )

