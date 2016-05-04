from tqdm import tqdm
import csv
from pprint import pprint as pp
import re
import os
from bs4 import BeautifulSoup
import sys

# Workaround for printing unicode stuff on Windows CMD (gokcen)
try:
	import win_unicode_console
	win_unicode_console.enable()
except ImportError:
	pass

# Setup a log to redirect useful (but very messy) informations to a file
import logging
logger = logging.getLogger('word_difference_method')
hdlr = logging.FileHandler('./word_difference_method.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

DUMP_LOG = False

# Bullshit detector.
# See: https://regex101.com/r/dT5xA1/2
# Basically counts number of stupid characters like "<", "*" etc. PLUS number of "numbers"
# If that number is high, most probably the text is actually a scanned "table" or "advertisement" that includes
# prices like ".-45" or just OCR errors like ".. ... ... *** << "
BULLSHIT_REGEX = re.compile(r"""([^ a-zA-Zàâæçéèêëïîôùûüÿ]+|[\d+])""")

def get_filtered_article_tuple(raw_article):
	'''
	Discards broken xml's (when it cannot find full_text etc.)
	and
	full_text's with less than 60 characters. Mostly titles.
	and
	full_text's with OCR errors less than %40 (????), or texts with tables (they usually contain so many numbers)
		(number of matched stuff < %40 of number of words)
	'''
	try:
		art_tpl = (
			raw_article.find("issue_date").text,
			raw_article.find("full_text").text,
			hash(raw_article.find("issue_date").text + raw_article.find("full_text").text)
			)
		if len(str(art_tpl[1])) > 60 and len(BULLSHIT_REGEX.findall(str(art_tpl[1]))) < 0.4*len(str(art_tpl[1]).split(' ')):
			return art_tpl
		else:
			if DUMP_LOG:
				logger.warning("Discarded text: " + art_tpl[1])
			return None
	except:
		return None

def get_month_lxml(year, month,folder="JDG"):
	'''
	Returns list of soup objects of given year and month from the package 'folder'
	'''
	file_path = "./data/{folder}/{year}/{month:0>2}.xml".format(month=month, year=year, folder=folder)
	try:
		soup = BeautifulSoup(open(file_path,encoding='utf-8'), "lxml")
	except FileNotFoundError:
		return []
	return soup.find_all("article")

def generate_csv_files(from_year,to_year,folder="JDG"): #years inclusive
	if not os.path.exists("csv"):
		os.makedirs("csv")
	
	#Convert xml's to csv		
	for year in range(from_year,to_year + 1):
		for month in tqdm(range(1, 13)):
			if os.path.isfile("./csv/%s/%d_%d.csv" % (folder, year, month)):
				continue
			with open("./csv/%s/%d_%d.csv" % (folder, year, month), 'w', newline='') as f:
				raw_articles = get_month_lxml(year, month, folder)
				articles = filter(lambda x: x is not None, map(get_filtered_article_tuple, raw_articles))
				if articles:
					writer = csv.writer(f, delimiter='\t')
					writer.writerows(articles)
		print("Year: %d Finished CSV writing" % year)
	pass

with open('french_words.txt', 'r') as f:
	to_be_removed = set(map(lambda x : x.strip().lower(), f.readlines()))

def get_ratio(left_paragraph, right_paragraph):
	# Summary of operations below:
	# Split to words, convert to lowercase, remove 1-char words, remove french stop words.
	left_set = set(filter(lambda x : len(x) > 1, map(lambda x : x.lower(), left_paragraph.split(' ')))) - to_be_removed
	right_set = set(filter(lambda x : len(x) > 1, map(lambda x : x.lower(), right_paragraph.split(' ')))) - to_be_removed

	return (float(len(left_set.intersection(right_set))),float(len(left_set.union(right_set))), left_set.intersection(right_set))





if __name__ == "__main__":
	# Uncomment the code below to generate CSV files.
	if len(sys.argv) == 3:
		from_yr = int(sys.argv[1])
		to_yr = int(sys.argv[2])
		print("Working from %d to %d" % (from_yr, to_yr))
		generate_csv_files(from_yr, to_yr,"GDL")
	exit()

	test_string = """
		L'armée française du commandant Lamy comprenait plus de 700 hommes depuis l'arrivée de la colonne Gentil ; leurs alliés baguirmiens comptaient au total 600 fusils et 200 cavaliers. Le tata (camp retranché) de Rabah (un carré de 800 m de côté adossé au Chari) était à 6 km en aval de Kousséri, en face du site actuel de Ndjamena. Il fallait ménager les susceptibilités et respecter le partage colonial décidé au traité de Berlin de 1885 : le camp de Rabah étant en territoire « allemand », Lamy s'adressa à Omar Sanda, héritier légitime du shehu Hashim de Bornou. Ce dernier donna officiellement à Gaourang de Baguirmi et à ses "alliés" toute licence pour chasser Rabah et le rétablir sur le trône.

		Sortant de Kousséri les Français formèrent 3 colonnes. Celle de droite commandée par le capitaine Joalland (mission Afrique Centrale) : 174 fusils, 1 canon de 80 ; celle du centre (mission Gentil), par le capitaine Robillot : 340 fusils, 2 canons de 80 ; celle de gauche (mission saharienne), par le commandant Reibell : 274 fusils, 1 canon de 42.

		Lamy attaqua le camp de Rabah sur 3 côtés, ne laissant libre que la berge du Chari. Après deux heures de fusillade et de canonnade on chargea, le tata fut enlevé et évacué par ses défenseurs en fuite. Rabah passa alors à la contre-attaque qui fut dévastatrice : Lamy fut mortellement touché par une balle, avec le capitaine de Cointet. Mais les Sénégalais arrêtèrent Rabah qui, blessé, s'enfuit, tandis que les fuyards qui tentaient de franchir le fleuve étaient fusillés dans le Chari.

		La tête de Rabah rapportée comme trophée
		La tête de Rabah rapportée comme trophée
		Au cours de la poursuite Rabah fut reconnu par un tirailleur de la mission Afrique Centrale, ancien déserteur de sa propre armée, qui l'acheva d'une balle dans la tête. Apprenant qu'il y avait une prime pour Rabah, il retourna sur le terrain et rapporta sa tête et sa main droite. Rabah fut unanimement identifié. Les Baguirmiens s'acharneront sur ses restes.
	"""
	results = []
	for year in range(1826,1950):
		for month in tqdm(range(1, 13)):
			with open("./csv/%d_%d.csv" % (year, month), 'r') as f:
				reader = csv.reader(f, delimiter="\t")
				results += [(line[0], get_ratio(test_string, line[1])) for line in reader]
		print("%d done" % year)
	results.sort(key=lambda x : x[1][0]/x[1][1], reverse=True)
	pp(results[:3])

	exit()


	# NOTE

	# I think we might not need a DB. Really. I found plain CSV files are really fast and we dont need to use SQL stuff.
	# For range queries (on dates) we just can depend on functions like get_month.
	# 2.7 GB set of XML files became ~1 GB CSV files. (XML tags & articles with OCR errors & very short articles like title's are REMOVED)
	# Also very fast to read and process. For now, CSV files are named like YEAR_MONTH.xml but If we decide that we don't need 'month' stuff
	# (we can still access the date information in article though) we can concatanate files in a year and processing them might be faster (?).