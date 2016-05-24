try:
	import ujson as json
except ImportError:
	import json

try:
	import win_unicode_console
	win_unicode_console.enable()
except:
	pass

from peters_spell_checker import correct
from tqdm import tqdm

if __name__ == "__main__":
	with open('1871.json', 'r') as infile:
		lst = json.load(infile)
	corrected_count = 0
	bad_count = 0
	ok_count = 0
	for word in tqdm(lst):
		corrected = correct(word)
		#if corrected != "BAD" and corrected!="OK":
		if corrected == "OK":
			ok_count += 1
		elif corrected == "BAD": 
			bad_count += 1
		else:
			corrected_count += 1
			#continue
			#print(word, '->', corrected)
		#correct(word)
	print("ok_count", ok_count)
	print("corrected_count", corrected_count)
	print("bad_count", bad_count)
	print("total", len(lst), ok_count+corrected_count+bad_count)