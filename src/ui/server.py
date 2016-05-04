from bottle import route, run, template, static_file, redirect, request
import itertools


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


try:
	import ujson as json
except ImportError:
	import json

#LOADING MODULE FROM UPPER DIR - hackish..
import sys, os
old_dir = os.path.abspath(os.curdir)
os.chdir('..')
sys.path.append(os.path.abspath(os.curdir))
from generate_word_buckets import give_results
os.chdir(old_dir)

#OK, HACK END



@route('/')
def index():
    redirect("/static/index.html")

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='static')

@route('/api', method='POST')
def process():
	text = request.forms.get('input') 
	results = give_results(text, 1800, 2000)
	return dict(data=[{
		"x": list(map(lambda x : x[0], results)),
		"y": list(map(lambda x : x[1][y_idx], results)),
	} for y_idx in range(5)])

@route('/about_dataset')
def about_dataset():
    redirect("/static/about_dataset.html")

@route('/api/about_dataset')
def about_dataset():

	with open("result", 'r') as infile:
		data = [line.split() for line in infile]
		d = dict()
		for k, g in itertools.groupby(data, lambda x: x[1][:4]):
			d[int(k)] = sum(map(lambda x: int(x[0]), g))

	x = []
	y = []
	with cd("../buckets/JDG"):
		for year in range(1800,2000):
			if not os.path.isfile("%d_stemmed.json" % year):
				continue
			with open("%d_stemmed.json" % year, 'r') as infile:
				obj = json.load(infile)
				if d[year]:
					x.append(year)
					y.append(float(obj["number_of_broken_words"])/d[year])
	return dict(data=[{
		"x": x,
		"y": y,
	}])

run(host='localhost', port=8080, reloader=True)