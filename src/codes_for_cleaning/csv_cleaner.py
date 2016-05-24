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
	import concurrent.futures
except:
	pass

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
	result = map(lambda x: correct_cached(x)[0], words_list)
	#broken = 0
	#good = 0
	#fixed = 0
	#for word in words_list:
	#	corrected_word, is_corrected = correct(word, CORRECTION_TRESHOLD)
	#	if corrected_word is None:
	#		broken += 1
	#	elif corrected_word and is_corrected:
	#		fixed += 1
	#	elif corrected_word and not is_corrected:
	#		good += 1
	#	result.append(corrected_word if corrected_word else word)
	#print("Gain %%", (len(set(words_list))-float(len(set(result))))/len(set(words_list))*100.0)
	#return (' '.join(result), good, fixed, broken)
	return ' '.join(result)

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
	for year, month in tqdm(list(product(year_list, month_list))):
		filename = "csv/{dataset}/{year}_{month}.csv".format(dataset=DATASET_STR, year=str(year), month=str(month))
		out_file = "cleaned_csv/{dataset}/{year}_{month}.csv".format(dataset=DATASET_STR, year=str(year), month=str(month))
		if not os.path.isfile(filename) or os.path.isfile(out_file) and os.path.getsize(out_file) > 5:
			continue
		fixed = []
		with open(filename) as f:
			reader = csv.reader(f,  delimiter='\t')
			#for row in reader:
				#result, good, num_fixed, broken = clean_article(row[1])
				#result = clean_article(row[1])
				#fixed.append([row[0], result])
				#print(good,fixed,broken)
			#with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
			#	fixed = executor.map(lambda x: [ x[0] , clean_article(x[1])], reader)
			fixed = list(map(lambda x: [ x[0] , clean_article(x[1])], reader))
		write_to_csv(fixed, out_file)
		print("\n",correct_cached.cache_info())
		#jobs.append((fixed, out_file))

		#if len(jobs) > 30:
		#	print("\nFlushing")
		#	for data, fname in jobs:
		#		write_to_csv(data,fname)
		#	jobs = []
		#	print("Finished")
