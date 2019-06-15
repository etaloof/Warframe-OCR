import sqlite3
from flask import Flask, render_template
application = Flask(__name__)


@application.route('/')
def index():
    db = sqlite3.connect('relicdb.sqlite3')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Relic")
    data = cursor.fetchall()
    return render_template('test.html', data=data)


@application.route('/table')
def tabledex():
    db = sqlite3.connect('relicdb.sqlite3')
    cursor = db.cursor()
    cursor.execute('''SELECT Relic.Name, Relic.Era, User.Pseudo, Relic.Quality, Relic.Quantity FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser''')
    data = cursor.fetchall()
    return render_template('table.html', data=data)


if __name__ == '__main__':
    application.run(debug=True)

