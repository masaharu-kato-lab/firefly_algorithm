import pathbuilder
import json
import pickle
import time
import settings

# ways = pickle.load(open("pickles/ways.pickle","rb"))

class Evaluator:

    def __init__(self):
        self.original_route = settings.CHECKPOINT_ORDERED
        self.ways = pickle.load(open("res/pickles/ways.pickle", "rb"))

    def build_route(self, route):
        return pathbuilder.route_builder(route, self.ways)

    def evaluate(self, route):
        return sum([p.T for p in self.build_route(route)[0]])

    def json_output(self, route, filename):
        data = {}
        data['times'] = []
        data['points'] = []
        data['checkpoints'] = []
        data['koord'] = []
        data['speed'] = []

        data['speed'].append(settings.SPEED)

        new_route = self.build_route(route)

        for p in new_route[0]:
            data['times'].append(p.T)
            data['points'].append(p.point)

        for checkpoint in new_route[1]:
            data['checkpoints'].append(checkpoint)

        for koord in self.original_route:
            data['koord'].append(koord)

        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=2)
