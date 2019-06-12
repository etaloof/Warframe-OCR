import sqlite3

db = sqlite3.connect('relicdb.sqlite3')
cursor = db.cursor()

cursor.execute('''CREATE TABLE if not exists User (
IDUser integer PRIMARY KEY AUTOINCREMENT,
Pseudo varchar
)''')

cursor.execute('''CREATE TABLE if not exists Relic (
IDRelic integer PRIMARY KEY AUTOINCREMENT,
Name varchar,
Era text,
IDOwner integer,
Quality text,
Quantity integer
)''')

cursor.execute('''CREATE TABLE if not exists RelicData (
IDRelic integer PRIMARY KEY AUTOINCREMENT
)''')


db.commit()
