import sqlite3
from collections import defaultdict

db = sqlite3.connect('relicdb.sqlite3')
cursor = db.cursor()
cursor.execute('''SELECT Relic.Name, Relic.Era, User.Pseudo, Relic.Quality, Relic.Quantity FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser GROUP BY Relic.Name, Relic.Era, Relic.Quality''')
results = cursor.fetchall()
print(results)
#data = defaultdict(list)

#for field1, field2, owner, status, quantity in results:
#    data[(field1, field2, status)].append((owner, quantity))

#for i in results:
#    print(data[(i[0], i[1], i[3])])
