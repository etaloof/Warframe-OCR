import sqlite3
from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def index():
    db = sqlite3.connect('relicdb.sqlite3')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Relic")
    data = cursor.fetchall()
    return render_template('test.html', data=data)


@app.route('/table')
def tabledex():
    db = sqlite3.connect('relicdb.sqlite3')
    cursor = db.cursor()
    cursor.execute('''SELECT Relic.Name, Relic.Era, User.Pseudo, Relic.Quality, Relic.Quantity FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser''')
    # cursor.execute("SELECT * FROM Relic")
    data = cursor.fetchall()
    return render_template('table.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)

