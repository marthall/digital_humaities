from tqdm import tqdm
import csv
from pprint import pprint as pp
from collections import Counter
import sys
import os
try:
	import ujson as json
except ImportError:
	import json
import math
from contextlib import contextmanager
# Workaround for printing unicode stuff on Windows CMD (gokcen)
try:
	import win_unicode_console
	win_unicode_console.enable()
except ImportError:
	pass

with open('french_words.txt', 'r') as f:
	to_be_removed = set(map(lambda x : x.strip().lower(), f.readlines()))

@contextmanager
def cd(path):
	old_dir = os.getcwd()
	os.chdir(path)
	try:
		yield
	finally:
		os.chdir(old_dir)

CWD = os.path.dirname(os.path.abspath(__file__))

def get_distances_between_sets(left_set, right_set):
	matching = float(len(left_set.intersection(right_set)))
	dice = (2.0*matching)/(len(left_set) + len(right_set))
	jaccard = matching/len(left_set.union(right_set))
	overlap = matching/(min(len(left_set),len(right_set)))
	cosine = matching/(math.sqrt(float(len(left_set)*len(right_set))))
	return [matching, dice, jaccard, overlap, cosine]

def text_to_wordlist(text):
	return [word for word in filter(lambda x : len(x) > 1, map(lambda x : x.lower().strip("0123456789().:-;}{[]!?*+$#^\\/_¨~@,<>\""), text.split())) if word not in to_be_removed]

def generate_bucket_files(from_yr, to_yr,folder="JDG"):
	if not os.path.exists("buckets"):
		os.makedirs("buckets")

	if not os.path.exists("buckets/%s" % folder):
		os.makedirs("buckets/%s" % folder)

	for year in range(from_yr,to_yr):
		word_list = []
		if os.path.exists('buckets/%s/%d.json' % (folder, year)) and os.path.getsize('buckets/%s/%d.json' % (folder, year)) > 100:
			print("%d already done" % year)
			continue
		for month in tqdm(range(1, 13)):
			if not os.path.exists("./csv/%s/%d_%d.csv" % (folder, year, month)):
				continue
			with open("./csv/%s/%d_%d.csv" % (folder, year, month), 'r') as f:
				reader = csv.reader(f, delimiter="\t")
				list_of_words = [text_to_wordlist(line[1]) for line in reader]
				word_list += sum(list_of_words, [])
		if word_list:
			with open('buckets/%s/%d.json' % (folder, year) , 'w') as outfile:
				#counted = Counter(word_list)
				#counted.subtract
				json.dump(list(set(word_list)), outfile, indent=4)
		else:
			print("\t%d looks empty..")
		print("%d done" % year)

def give_year_similiarity(year, left_set):
	with cd(CWD):
		with open('buckets/JDG/%d.json' % year, 'r') as infile:
			lst = json.load(infile)
			if not lst:
				return None
			right_set = set(lst)
			return get_distances_between_sets(left_set, right_set)

def give_results(input_text, from_year, to_year):
	left_set = set(text_to_wordlist(input_text))

	results = []
	for year in range(from_year,to_year):
		try:
			resp = give_year_similiarity(year, left_set)
			if resp:
				results.append((year,resp))
		except:
			pass
	return results


if __name__ == "__main__":
	if len(sys.argv) == 4:
		from_yr = int(sys.argv[1])
		to_yr = int(sys.argv[2])
		if sys.argv[3] in ["GDL", "JDG"]:
			print("Working from %d to %d [%s]" % (from_yr, to_yr, sys.argv[3]))
			generate_bucket_files(from_yr, to_yr,sys.argv[3])
		else:
			print("Dude, it must be either GDL or JDG..")

	test_string = """
		L'armée française du commandant Lamy comprenait plus de 700 hommes depuis l'arrivée de la colonne Gentil ; leurs alliés baguirmiens comptaient au total 600 fusils et 200 cavaliers. Le tata (camp retranché) de Rabah (un carré de 800 m de côté adossé au Chari) était à 6 km en aval de Kousséri, en face du site actuel de Ndjamena. Il fallait ménager les susceptibilités et respecter le partage colonial décidé au traité de Berlin de 1885 : le camp de Rabah étant en territoire « allemand », Lamy s'adressa à Omar Sanda, héritier légitime du shehu Hashim de Bornou. Ce dernier donna officiellement à Gaourang de Baguirmi et à ses "alliés" toute licence pour chasser Rabah et le rétablir sur le trône.

		Sortant de Kousséri les Français formèrent 3 colonnes. Celle de droite commandée par le capitaine Joalland (mission Afrique Centrale) : 174 fusils, 1 canon de 80 ; celle du centre (mission Gentil), par le capitaine Robillot : 340 fusils, 2 canons de 80 ; celle de gauche (mission saharienne), par le commandant Reibell : 274 fusils, 1 canon de 42.

		Lamy attaqua le camp de Rabah sur 3 côtés, ne laissant libre que la berge du Chari. Après deux heures de fusillade et de canonnade on chargea, le tata fut enlevé et évacué par ses défenseurs en fuite. Rabah passa alors à la contre-attaque qui fut dévastatrice : Lamy fut mortellement touché par une balle, avec le capitaine de Cointet. Mais les Sénégalais arrêtèrent Rabah qui, blessé, s'enfuit, tandis que les fuyards qui tentaient de franchir le fleuve étaient fusillés dans le Chari.

		La tête de Rabah rapportée comme trophée
		La tête de Rabah rapportée comme trophée
		Au cours de la poursuite Rabah fut reconnu par un tirailleur de la mission Afrique Centrale, ancien déserteur de sa propre armée, qui l'acheva d'une balle dans la tête. Apprenant qu'il y avait une prime pour Rabah, il retourna sur le terrain et rapporta sa tête et sa main droite. Rabah fut unanimement identifié. Les Baguirmiens s'acharneront sur ses restes.
	"""
	import enchant
	d = enchant.Dict("fr_FR")


	#from pprint import pprint as pp
	#left_set = set(text_to_wordlist(test_string))
	with open("test/1871.json", "r") as f:
		words = json.load(f)
	
	for word in words:
		w = word[0].upper()+word[1:]
		if not d.check(w):
			print(w, ">>>", d.suggest(w))

	exit()	



	#results.sort(key=lambda x : x[1][0]/x[1][1], reverse=True)
