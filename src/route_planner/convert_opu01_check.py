import pickle
import sys

def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else 'res/pathdata/opu.dict.pickle'
    data = pickle.load(open(data_path, mode='rb'))
    print(type(data))


if __name__ == "__main__":
    main()
