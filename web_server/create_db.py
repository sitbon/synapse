from pysqlite2 import dbapi2 as sqlite3

db = sqlite3.connect('dress.db')
db.execute("CREATE TABLE proximity (id INTEGER PRIMARY KEY, value INTEGER NOT NULL)")
db.commit()

db.execute("CREATE TABLE heartrate (id INTEGER PRIMARY KEY, value INTEGER NOT NULL)")
db.commit()

db.execute("CREATE TABLE attention (id INTEGER PRIMARY KEY, value INTEGER NOT NULL)")
db.commit()

db.execute("CREATE TABLE images (id INTEGER PRIMARY KEY, url TEXT NOT NULL)")
db.commit()