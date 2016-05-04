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
	broken = 0
	good = 0
	fixed = 0
	for word in words_list:
		corrected_word, is_corrected = correct(word, CORRECTION_TRESHOLD)
		if corrected_word is None:
			broken += 1
		elif corrected_word and is_corrected:
			fixed += 1
		elif corrected_word and not is_corrected:
			good += 1
		result.append(corrected_word if corrected_word else word)
	#print("Gain %%", (len(set(words_list))-float(len(set(result))))/len(set(words_list))*100.0)
	return (''.join(result), good, fixed, broken)


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
				result, good, num_fixed, broken = clean_article(row[1])
				fixed.append([row[0], result])
				#print(good,fixed,broken)
		out_file = "cleaned_csv/{dataset}/{year}_{month}.csv".format(dataset=DATASET_STR, year=str(year), month=str(month))
		with open(out_file, 'w', encoding='utf-8') as f:
			csv_writer = csv.writer(f, delimiter='\t')
			csv_writer.writerows(fixed)
