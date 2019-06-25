import sqlite3
from flask import Flask, render_template
application = Flask(__name__)


@application.route('/test')
def index():
    db = sqlite3.connect('relicdb.sqlite3')
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM Relic''')
    data = cursor.fetchall()
    return render_template('test.html', data=data)


@application.route('/')
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
    
    return render_template('table.html', data=results_f)


if __name__ == '__main__':
    application.run(host='0.0.0.0')

