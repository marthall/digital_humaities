from bs4 import BeautifulSoup
import sqlite3

def get_month(year, month):
	file_path = "./data/JDG/{year}/{month:0>2}.xml".format(month=month, year=year)
	soup = BeautifulSoup(open(file_path), "html.parser")
	return soup.find_all("article")

def get_year(year):
	articles = [get_month(year, month) for month in range(1,5)]
	return [a for month in articles for a in month]

class Article(object):
	def __init__(self, soup_object):
		self.text = soup_object.find("full_text").text
		self.data = soup_object.find("issue_date").text

# articles = [Article(a) for a in get_month(1992, 1)]

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.execute(''' 	select * from articles ''')

article = c.fetchone()

conn.commit()
c.close()

print(article)

