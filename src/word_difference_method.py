import sqlite3
from tqdm import tqdm
import csv
from pprint import pprint as pp
import re
import os
from bs4 import BeautifulSoup

DATABASE_NAME = "data_with_hash.db"

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
			logger.warning("Discarded text: " + art_tpl[1])
			return None
	except:
		return None

def get_month_lxml(year, month):
	file_path = "./data/JDG/{year}/{month:0>2}.xml".format(month=month, year=year)
	soup = BeautifulSoup(open(file_path,encoding='utf-8'), "lxml")
	return soup.find_all("article")


def create_database_with_hash_column(): #TODO remove this if we decide to avoid SQL stuff
	if not os.path.isfile("./" + DATABASE_NAME):
		conn = sqlite3.connect(DATABASE_NAME)
		c = conn.cursor()
		c.execute('''CREATE TABLE articles
						(issue_date date, content text, hash_val integer UNIQUE) ''')
		conn.commit()
		c.close()
	pass

def generate_csv_files(from_year,to_year): #years inclusive
	if not os.path.exists("csv"):
		os.makedirs("csv")
	
	#Convert xml's to csv		
	for year in range(from_year,to_year + 1):
		for month in tqdm(range(1, 13)):
			if os.path.isfile("./csv/%d_%d.csv" % (year, month)):
				continue
			with open("./csv/%d_%d.csv" % (year, month), 'w', newline='') as f:
				raw_articles = get_month_lxml(year, month)
				articles = filter(lambda x: x is not None, map(get_filtered_article_tuple, raw_articles))
				writer = csv.writer(f, delimiter='\t')
				writer.writerows(articles)
		print("Year: %d Finished CSV writing" % year)
	pass

with open('french_words.txt', 'r') as f:
	to_be_removed = set(map(lambda x : x.strip().lower(), f.readlines()))
	#print(to_be_removed)

def get_ratio(left_paragraph, right_paragraph):
	# Summary of operations below:
	# Split to words, convert to lowercase, remove 1-char words, remove french stop words.
	left_set = set(filter(lambda x : len(x) > 1, map(lambda x : x.lower(), left_paragraph.split(' ')))) - to_be_removed
	right_set = set(filter(lambda x : len(x) > 1, map(lambda x : x.lower(), right_paragraph.split(' ')))) - to_be_removed

	return (float(len(left_set.intersection(right_set))),float(len(left_set.union(right_set))), left_set.intersection(right_set))

if __name__ == "__main__":
	# Uncomment the code below to generate CSV files.
	# generate_csv_files(1921, 1960)

	test_string = """
		Numéro littéraire et économique GENEVE , 31 juillet 1921 Les Feux sur la montagne Ce soir , les feux allumés sur les montagnes répondront à ceux qui brilleront dans la plaine . De Baie à Genève , de Lugano à Delémont , les cloches diront aux Suisses que le 1 août 1291 retentit encore dans les cœurs . Et l'étranger , respectueux de cette coutume très simple de célébrer le plus grand anniversaire de l'histoire helvétique , mêlera peut-être ses chants aux nôtres . Ce sera émouvant et beau . 'Mais l'émotion d'une minute fugitive ni la beauté d'un héroïque passé ne constituent un Peuple . Elles ne lui donnent pas sa vitalité . Elles l'aident , assurément , mais ne seraient que les béquilles du sentimentalisme si la Suisse ne trouvait en elle-même des appuis plus sûrs . A coups de lance et d'épée , luttant contre ceux-ci un jour , contre ceux-là le lendemain , unis dans leurs aspirations démocratiques et soumis au pacte qu'ils avaient Juré , . armant non seulement leurs
	"""
	results = []
	for year in range(1921,1926):
		for month in tqdm(range(1, 13)):
			with open("./csv/%d_%d.csv" % (year, month), 'r') as f:
				reader = csv.reader(f, delimiter="\t")
				results += [(line[1], get_ratio(test_string, line[1])) for line in reader]
	results.sort(key=lambda x : x[1][0]/x[1][1], reverse=True)
	pp(results[:3])

	exit()


	# NOTE

	# I think we might not need a DB. Really. I found plain CSV files are really fast and we dont need to use SQL stuff.
	# For range queries (on dates) we just can depend on functions like get_month.
	# 2.7 GB set of XML files became ~1 GB CSV files. (XML tags & articles with OCR errors & very short articles like title's are REMOVED)
	# Also very fast to read and process. For now, CSV files are named like YEAR_MONTH.xml but If we decide that we don't need 'month' stuff
	# (we can still access the date information in article though) we can concatanate files in a year and processing them might be faster (?).








	##### THE CODE BELOW was WRITTEN before CSV stuff. Ignore them. ####

	# Create DB if not already here
	# create_database_with_hash_column()
	# Check currently available date's
	# conn = sqlite3.connect(DATABASE_NAME)
	# cur = conn.cursor()
	#cur.execute(''' SELECT issue_date from articles order by issue_date LIMIT 500 ''')
	#pp(cur.fetchall())

	# for year in range(1921,1925):
	# 	articles = []
	# 	total_article_count = 0
	# 	for month in tqdm(range(1, 13)):
	# 		raw_articles = get_month(year, month)
	# 		total_article_count += len(raw_articles)
	# 		articles += list(filter(lambda x: x is not None, map(get_filtered_article_tuple, raw_articles)))
	# 	print("Parsed articles: %5d, Removed articles: %5d" % (total_article_count, total_article_count-len(articles)))
	# 	cur.executemany(''' INSERT or IGNORE into articles (issue_date, content, hash_val) values (?, ?, ?)''', articles)
	# 	cur.commit()
	# 	print("Tried to insert: %5d, Actually inserted: %5d" % (len(articles), cur.rowcount))
	# 	print("%d Finished" % year)