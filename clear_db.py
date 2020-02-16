import sqlite3

db = sqlite3.connect('relicdb.sqlite3')
cursor = db.cursor()

cursor.execute('''DELETE FROM Relic''')

db.commit()
