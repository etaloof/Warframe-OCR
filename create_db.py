import sqlite3

db = sqlite3.connect('relicdb')
cursor = db.cursor()

cursor.execute('''CREATE TABLE User (
IDUser integer PRIMARY KEY AUTOINCREMENT,
Pseudo varchar
)''')

cursor.execute('''CREATE TABLE Relic (
IDRelic integer PRIMARY KEY AUTOINCREMENT,
Name varchar,
Era text,
IDOwner integer,
Quantity integer
)''')

cursor.execute('''CREATE TABLE RelicData (
IDRelic integer PRIMARY KEY AUTOINCREMENT
)''')


db.commit()
