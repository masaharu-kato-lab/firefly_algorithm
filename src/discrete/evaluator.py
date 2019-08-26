import pathbuilder
import json
import pickle
import time
import settings

# ways = pickle.load(open("pickles/ways.pickle","rb"))

class Evaluator:

    def __init__(self):
        self.ways = pickle.load(open("res/pickles/ways.pickle", "rb"))


    def evaluate(self, route):
        # print(route)
        new_route = pathbuilder.route_builder(route, self.ways)[0]
        return sum([p.T for p in new_route])
