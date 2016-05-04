try:
	import ujson as json
except ImportError:
	import json

try:
	import win_unicode_console
	win_unicode_console.enable()
except:
	pass

from peters_spell_checker import correct, words
from tqdm import tqdm
from itertools import product
import os
import csv

CORRECTION_TRESHOLD = 60

def clean_article(article_str):
	'''
	Doesn't removes duplicates.
	Returns (list_of_good_strings, number_of_good,number_of_fixed,number_of_removed)
	'''
	words_list = words(article_str)
	result = []
	removed = 0
	good = 0
	fixed = 0
	for word in words_list:
		corrected_word, is_corrected = correct(word, CORRECTION_TRESHOLD)
		if corrected_word is None:
			removed += 1
		else:
			result.append(corrected_word)
			if corrected_word and is_corrected:
				fixed += 1
			elif corrected_word and not is_corrected:
				good += 1
	return (result, good, fixed, removed)


if __name__ == "__main__":
	os.chdir("..")
	year_list = range(1826, 1999)
	month_list = range(1,13)
	DATASET_STR = "JDG" #or "GDL"
	for year, month in tqdm(product(year_list, month_list)):
		filename = "csv/{dataset}/{year}_{month}.csv".format(dataset=DATASET_STR, year=str(year), month=str(month))
		if not os.path.isfile(filename):
			continue
		fixed = []
		with open(filename) as f:
			reader = csv.reader(f,  delimiter='\t')
			for row in reader:
				fixed.append([])