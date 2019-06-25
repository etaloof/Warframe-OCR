import sqlite3
from collections import defaultdict

db = sqlite3.connect('relicdb.sqlite3')
cursor = db.cursor()
cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser GROUP BY Relic.Name, Relic.Era, Relic.Quality''')
results = cursor.fetchall()

for element in results:
    a, b = element[-2:]
    my_new_string = ' | '.join([f'{owner} ({value})' for owner, value in zip(a.split(','), b.split(','))])
    my_new_tuple = (*element[:-2], my_new_string)
    print(my_new_tuple)

# tuple1 = ('A1', 'Meso', 'Intacte', 'kenexey,Demokdawa', '1,5')




