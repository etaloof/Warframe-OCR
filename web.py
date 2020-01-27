import sqlite3
from flask import Flask, render_template
application = Flask(__name__)

@application.route('/')
def index():
    db = sqlite3.connect('relicdb.sqlite3')
    cursor = db.cursor()
    cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser GROUP BY Relic.Name, Relic.Era, Relic.Quality''')
    # cursor.execute('''SELECT Relic.Name, Relic.Era, User.Pseudo, Relic.Quality, Relic.Quantity FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser''')
    data = cursor.fetchall()
    results_f = []
    for element in data:
        a, b = element[-2:]
        new_string = ' | '.join([f'{owner} ({value})' for owner, value in zip(a.split(','), b.split(','))])
        new_tup = (*element[:-2], new_string)
        new_l = list(new_tup)
        results_f.append(new_l)

    for element in results_f: # Pour chaque row
        list1 = []
        cursor.execute('''SELECT c_1, c_2, c_3, u_1, u_2, r_1 FROM RelicData WHERE Era = ? AND Name = ?''', (element[1], element[0],))
        result = cursor.fetchone() #tuple
        list1.extend(result)
        for ele in result:
            cursor.execute('''SELECT PricePlat, PriceDucats FROM PrimePartData WHERE Name = ?''', (ele,))
            result2 = cursor.fetchone() #tuple
            list1.extend(result2)
            
        element.extend(list1)

    return render_template('relic.html', data=results_f)
    
    # Organization of one line :
    # 0 : relic name
    # 1 : relic era
    # 2 : quality
    # 3 : posesseurs
    # 4 : common 1
    # 5 : common 2
    # 6 : common 3
    # 7 : uncommon 1
    # 8 : uncommon 2
    # 9 : rare 1
    # 10 : common 1 plat
    # 11 : common 1 ducats
    # 12 : common 2 plat
    # 13 : common 2 ducats
    # 14 : common 3 plat
    # 15 : common 3 ducats
    # 16 : uncommon 1 plat
    # 17 : uncommon 1 ducats
    # 18 : uncommon 2 plat
    # 19 : uncommon 2 ducats
    # 20 : rare 1 plat
    # 21 : rare 1 ducats


@application.route('/old')
def tabledex():
    db = sqlite3.connect('relicdb.sqlite3')
    cursor = db.cursor()
    cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser GROUP BY Relic.Name, Relic.Era, Relic.Quality''')
    # cursor.execute('''SELECT Relic.Name, Relic.Era, User.Pseudo, Relic.Quality, Relic.Quantity FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser''')
    data = cursor.fetchall()
    results_f = []
    for element in data:
        a, b = element[-2:]
        new_string = ' | '.join([f'{owner} ({value})' for owner, value in zip(a.split(','), b.split(','))])
        new_tup = (*element[:-2], new_string)
        results_f.append(new_tup)

    return render_template('oldtable.html', data=results_f)


if __name__ == '__main__':
    application.run(host='0.0.0.0')

