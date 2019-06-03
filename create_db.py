import sqlite3

db = sqlite3.connect('relicdb')
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
Quantity integer
)''')

cursor.execute('''CREATE TABLE if not exists RelicData (
IDRelic integer PRIMARY KEY AUTOINCREMENT
)''')


db.commit()
