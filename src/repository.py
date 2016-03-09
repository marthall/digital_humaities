
import sqlite3
conn = sqlite3.connect("data.db")
# c = conn.cursor()

# c.execute("select count(*) from articles")

# print(c.fetchone())

for row in conn.execute("select issue_date, content from articles"):
	print(row)