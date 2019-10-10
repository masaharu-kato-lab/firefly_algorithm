import pickle
import argparse

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('-i', '--input', type=str, required=True, help='Input binary pickle file.')
    args = argp.parse_args()

    with open(args.input, mode='rb') as f:
        out_bin = pickle.load(f)

    print(out_bin)


if __name__ == '__main__':
    main()
