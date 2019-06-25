import sqlite3
from collections import defaultdict

db = sqlite3.connect('relicdb.sqlite3')
cursor = db.cursor()
cursor.execute('''SELECT Relic.Name, Relic.Era, User.Pseudo, Relic.Quality, Relic.Quantity, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser GROUP BY Relic.Name, Relic.Era, Relic.Quality''')
results = cursor.fetchall()

for i in results:
    print('Relique ' + i[1] + ' ' + i[0] + ' ' + i[3] + ' possédée par ' + i[5].split(',')[0] + ' ' + i[6])
