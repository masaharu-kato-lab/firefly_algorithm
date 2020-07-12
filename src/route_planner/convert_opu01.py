import pickle
import json
import sys
import os
import map_converter

def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else 'res/pathdata/opu.pickle'
    bdata = pickle.load(open(data_path, mode='rb'))

    data = {
        'world'      : bdata.world,
        'checkpoints': bdata.default_targets,
        'depots'     : bdata.starting_point,
        'paths'      : {key_pts: [(pt[1], pt[0]) for pt in pts_and_cnt[0]] for key_pts, pts_and_cnt in bdata.paths.items()},
        'path_counts': {key_pts: pts_and_cnt[1] for key_pts, pts_and_cnt in bdata.paths.items()},
    }

    # json.dump(dict_data, open(os.path.splitext(data_path)[0] + '.json', mode='w'))
    pickle.dump(data, open(os.path.splitext(data_path)[0] + '.dict.pickle', mode='wb'))


if __name__ == "__main__":
    main()
