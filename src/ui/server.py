from bottle import route, run, template, static_file, redirect, request
import itertools


# class cd:
#     """Context manager for changing the current working directory"""
#     def __init__(self, newPath):
#         self.newPath = os.path.expanduser(newPath)

#     def __enter__(self):
#         self.savedPath = os.getcwd()
#         os.chdir(self.newPath)

#     def __exit__(self, etype, value, traceback):
#         os.chdir(self.savedPath)


try:
	import ujson as json
except ImportError:
	import json

import sys, os,csv
from backend.web_helper import get_naive_bayes


@route('/')
def index():
    redirect("/static/index.html")

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='static')

@route('/api', method='POST')
def process():
	# results = give_results(text, 1800, 2000)
	# dummy = ["matching: |X ∩ Y|", "dice: 2|X ∩ Y|/(|X| + |Y|)", "jaccard: |X ∩ Y|/|X ∪ Y|", "overlap: |X ∩ Y|/min(|X|,|Y|)", "cosine: |X ∩ Y|/sqrt(|X|*|Y|)"]
	# return dict(data=[{
	# 	"x": list(map(lambda x : x[0], results)),
	# 	"y": list(map(lambda x : x[1][y_idx], results)),
	# 	"name": dummy[y_idx]
	# } for y_idx in range(5)])

	text = request.forms.get('input') 
	years, probabilities = get_naive_bayes(text)

	return dict(data=[{
		"x": years,
		"y": probabilities,
		"name": "Naive Bayes prediction"
	}])




@route('/about_dataset')
def about_dataset():
    redirect("/static/about_dataset.html")

@route('/api/about_dataset')
def about_dataset():
	with open('after_cleaning_information.json', "r") as f:
		return json.load(f)


@route('/api/about_spellcheck')
def about_spellcheck():

	data = []
	for fname in ["JDG", "GDL"]:
		with open(fname + ".csv", 'r') as infile:
			reader = list(csv.reader(infile,  delimiter='\t'))
			dates = list(map(lambda x : x[0], reader))
			unique_before = list(map(lambda x : float(x[1]), reader))
			unique_after = list(map(lambda x : float(x[2]), reader))
			gain = list(map(lambda x : float(float(x[1])-float(x[2]))/float(x[1])*100.0, reader))
			good = list(map(lambda x : float(x[3]), reader))
			fixed = list(map(lambda x : float(x[4]), reader))
			dummy = {
				'unique_after': unique_after,
				'unique_before': unique_before,
				'gain': gain,
				'good': good,
				'fixed': fixed
			}
			for k,v in dummy.items():
				data.append({
					'name': fname + k,
					'y': v,
					'x': dates
					})
		
	
	return dict(data=data)


run(host='localhost', port=8000, reloader=True)
