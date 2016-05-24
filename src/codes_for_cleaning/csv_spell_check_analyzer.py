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
import sys

try:
	from peters_spell_checker import open
	print("Py2 patched open")
except:
	pass 

from functools import lru_cache

correct_cached = lru_cache(maxsize=None)(correct)

CORRECTION_TRESHOLD = 60

def clean_article(article_str):
	'''
	Doesn't removes duplicates.
	Returns (list_of_good_strings, number_of_good,number_of_fixed,number_of_removed)
	'''
	words_list = words(article_str)
	result = []
	#result = map(lambda x: correct_cached(x)[0], words_list)
	broken = 0
	good = 0
	fixed = 0
	for word in words_list:
		corrected_word, is_corrected = correct_cached(word, CORRECTION_TRESHOLD)
		if corrected_word is None:
			broken += 1
		elif corrected_word and is_corrected:
			fixed += 1
		elif corrected_word and not is_corrected:
			good += 1
		result.append(corrected_word if corrected_word else word)
	unique_words_before = float(len(set(words_list)))
	unique_words_after = float(len(set(result)))
	#print("Gain %%", (unique_words_before-unique_words_after)/unique_words_before*100.0)
	return (unique_words_before, unique_words_after, good, fixed)
	#return ' '.join(result)

jobs = []
def write_to_csv(data,fname):
	with open(fname, 'w', encoding='utf-8') as f:
		csv_writer = csv.writer(f, delimiter='\t')
		csv_writer.writerows(data)

if __name__ == "__main__":
	from_yr = int(sys.argv[1])
	to_yr = int(sys.argv[2])
	os.chdir("..")
	year_list = range(from_yr, to_yr)
	month_list = range(1,13)
	DATASET_STR = sys.argv[3] #or "GDL"
	final_data = []
	from operator import add
	for year, month in tqdm(list(product(year_list, month_list))):
		filename = "csv/{dataset}/{year}_{month}.csv".format(dataset=DATASET_STR, year=str(year), month=str(month))
		if not os.path.isfile(filename):
			continue
		with open(filename) as f:
			reader = csv.reader(f,  delimiter='\t')
			fixed = list(map(lambda x: list(clean_article(x[1])), reader))
			final_data.append([str(year) + "-" + str(month)] + [sum(x) for x in zip(*fixed)])
		print("\n",correct_cached.cache_info())
	write_to_csv(final_data, "final.csv")
		#jobs.append((fixed, out_file))

		#if len(jobs) > 30:
		#	print("\nFlushing")
		#	for data, fname in jobs:
		#		write_to_csv(data,fname)
		#	jobs = []
		#	print("Finished")
