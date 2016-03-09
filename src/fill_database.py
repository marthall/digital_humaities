from bs4 import BeautifulSoup
import sqlite3
from tqdm import tqdm

def get_month(year, month):
	file_path = "./data/JDG/{year}/{month:0>2}.xml".format(month=month, year=year)
	soup = BeautifulSoup(open(file_path), "html.parser")
	return soup.find_all("article")

def get_article_tuple(raw_article):
	return (
		raw_article.find("full_text").text,
		raw_article.find("issue_date").text
		)


conn = sqlite3.connect("data.db")

for month in tqdm(range(1, 13)):
	raw_articles = get_month(1992, month)
	articles = map(get_article_tuple, raw_articles)
	conn.executemany("insert into articles (issue_date, content) values (?, ?)", articles)

conn.commit()
