import sqlite3

db = sqlite3.connect('relicdb.sqlite3')
print('[Init] Connexion a la db réussie !')


# Return actual quantity for a specific relic of an owner
def check_relic_quantity(a1, a2, a3, owner):
    cursor = db.cursor()
    cursor.execute('''SELECT Quantity FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (a2, a1, a3, check_user_exist(owner),))
    result = cursor.fetchone()
    return result[0]


# Check if user exist in db. If not exist, create it. If exist, return his "IDUser" index
def check_user_exist(owner):
    cursor = db.cursor()
    cursor.execute('''SELECT IDUser FROM User WHERE Pseudo = ?''', (owner,))
    result = cursor.fetchone()
    if result:
        print('L\'utilisateur existe déja !')
        return result[0]
    else:
        print('L\'utilisateur n\'existe pas !')
        cursor.execute('''INSERT INTO User (Pseudo) VALUES (?)''', (owner,))
        db.commit()
        return cursor.lastrowid


# Add a relic to the DB using INSERT/UPDATE
def add_relic_to_db(a1, a2, a3, a4, owner):
    cursor = db.cursor()
    relic_owner = check_user_exist(owner)
    cursor.execute('''SELECT IDRelic FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (a2, a1, a3, relic_owner,))
    result = cursor.fetchone()
    if result:
        print('La relique existe déja !')
        cursor.execute('''UPDATE Relic SET Quantity = Quantity + ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (a4, a2, a1, a3, relic_owner,))
    else:
        cursor.execute('''INSERT INTO Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (?,?,?,?,?)''', (a1, a2, a3, a4, relic_owner))
    db.commit()


# Delete a relic on the DB using DELETE/UPDATE
def del_relic_on_db(a1, a2, a3, a4, owner):
    cursor = db.cursor()
    relic_owner = check_user_exist(owner)
    cursor.execute('''SELECT IDRelic FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (a2, a1, a3, relic_owner,))
    result = cursor.fetchone()
    if result:
        print('La relique existe bel et bien !')
        cursor.execute('''UPDATE Relic SET Quantity = Quantity - ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (a4, a2, a1, a3, relic_owner,))
        db.commit()
        return True
    else:
        return 'Tu ne peux pas supprimer ce que tu ne possèdes pas, Tenno !'
