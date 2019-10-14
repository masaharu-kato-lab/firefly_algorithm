import matplotlib.pyplot as plt
import matplotlib as mpl
import pickle

def main():

    with open('res/pathdata/opu.pickle', mode='rb') as f:
        mapper = pickle.load(f)

    plt.imshow(mapper.world, interpolation="none", cmap=mpl.colors.ListedColormap(['white', 'black']))

    plt.show()


if __name__ == '__main__':
    main()
