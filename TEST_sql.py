import sqlite3
from collections import defaultdict

db = sqlite3.connect('relicdb.sqlite3')
cursor = db.cursor()
cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser GROUP BY Relic.Name, Relic.Era, Relic.Quality''')
results = cursor.fetchall()
results_f = []

for element in results:
    a, b = element[-2:]
    new_string = ' | '.join([f'{owner} ({value})' for owner, value in zip(a.split(','), b.split(','))])
    new_tup = (*element[:-2], new_string)
    results_f.append(new_tup)

# tuple1 = ('A1', 'Meso', 'Intacte', 'kenexey,Demokdawa', '1,5')




