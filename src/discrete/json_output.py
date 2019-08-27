import json
import pickle
import time
import settings


def jsonBuilder(new_route, route, routeBase, filename):
	data = {}
	data['times'] = []
	data['points'] = []
	data['checkpoints'] = []
	data['koord'] = []
	data['speed'] = []

	data['speed'].append(settings.SPEED)

	for p in new_route:
		data['times'].append(p.T)
		data['points'].append(p.point)

	for checkpoint in route:
		data['checkpoints'].append(checkpoint)

	for koord in routeBase:
		data['koord'].append(koord)

	with open(filename, 'w', encoding='utf-8') as outfile:
		json.dump(data, outfile, ensure_ascii=False, indent=2)


