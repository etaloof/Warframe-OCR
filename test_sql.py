import sqlite3
from collections import defaultdict

db = sqlite3.connect('relicdb.sqlite3')
cursor = db.cursor()
cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser GROUP BY Relic.Name, Relic.Era, Relic.Quality''')
results = cursor.fetchall()

# for i in results:

tuple1 = ('A1', 'Meso', 'Intacte', 'kenexey,Demokdawa', '1,5')

tuple_f = (tuple1[0], tuple1[1], tuple1[2], tuple1[3].split(",")[0] + '(' + tuple1[4].split(",")[0] + ')' + ' | ' + tuple1[3].split(",")[0] + '(' + tuple1[4].split(",")[0] + ')')

print(tuple_f)

result_list = list_of_lists = [list(elem) for elem in results]

print(result_list)

