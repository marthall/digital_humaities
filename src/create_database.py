import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.execute('''	create table articles
				(issue_date date, content text) ''')

c.execute('''	insert into articles
				values ('2016-03-09', 'Hello World') ''')

conn.commit()
c.close()