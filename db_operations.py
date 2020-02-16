import sqlite3

db = sqlite3.connect('relicdb.sqlite3')
print('[Init] Connexion a la db réussie !')


# Return actual quantity for a specific relic of an owner
def check_relic_quantity(era, name, quality, owner):
    cursor = db.cursor()
    cursor.execute('''SELECT Quantity FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, check_user_exist(owner),))
    result = cursor.fetchone()
    return result[0]


# Check if user exist in db. If not exist, create it. If exist, return his "IDUser" index
def check_user_exist(owner):
    cursor = db.cursor()
    cursor.execute('''SELECT IDUser FROM User WHERE Pseudo = ?''', (owner,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute('''INSERT INTO User (Pseudo) VALUES (?)''', (owner,))
        db.commit()
        return cursor.lastrowid


# Add a relic to the DB using INSERT/UPDATE
def add_relic_to_db(era, name, quality, quantity, owner):
    cursor = db.cursor()
    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE Relic SET Quantity = Quantity + ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (quantity, name, era, quality, relic_owner,))
    else:
        cursor.execute('''INSERT INTO Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (?,?,?,?,?)''', (era, name, quality, quantity, relic_owner))
    db.commit()


# Delete a relic on the DB using UPDATE
def del_relic_on_db(era, name, quality, quantity, owner):
    cursor = db.cursor()
    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic, Quantity FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if (result[1] - quantity) < 0:
        cursor.execute('''UPDATE Relic SET Quantity = 0 WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))
        db.commit()
        return True
    elif result:
        cursor.execute('''UPDATE Relic SET Quantity = Quantity - ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (quantity, name, era, quality, relic_owner,))
        db.commit()
        return True
    else:
        return 'Tu ne peux pas supprimer une relique que tu ne possèdes pas, Tenno !'


# Refine an already owned relic
def refine_relics(era, name, quality, quantity, owner):
    cursor = db.cursor()
    relic_owner = check_user_exist(owner)
    cursor.execute('''SELECT IDRelic FROM Relic WHERE Name = ? AND Era = ? AND Quality = 'Intacte' AND IDOwner = ? AND Quantity >= ?''', (name, era, relic_owner, quantity))
    result = cursor.fetchone()
    print(result)
    if result:
        print('La relique existe et peut être raffinnée')
        cursor.execute('''UPDATE Relic SET Quantity = Quantity - ? WHERE Name = ? AND Era = ? AND Quality = 'Intacte' AND IDOwner = ?''', (quantity, name, era, relic_owner,))
        # TestQuery
        cursor.execute('''SELECT IDRelic FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))
        result = cursor.fetchone()
        if result:
            cursor.execute('''UPDATE Relic SET Quantity = Quantity + ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (quantity, name, era, quality, relic_owner,))
        else:
            cursor.execute('''INSERT INTO Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (?,?,?,?,?)''', (era, name, quality, quantity, relic_owner))
        db.commit()
        return True
    else:
        return 'Tu ne peux pas raffiner une relique que tu ne possèdes pas, Tenno !'


# Add relic from screen and update the quantity if already exist
def relic_from_screen(era, name, quality, quantity, owner):
    cursor = db.cursor()
    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE Relic SET Quantity = Quantity + ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (quantity, name, era, quality, relic_owner,))
    else:
        cursor.execute('''INSERT INTO Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (?,?,?,?,?)''', (era, name, quality, quantity, relic_owner))
    db.commit()


# Add relic from screen and overwrite the quantity if already exist
def relic_from_screen_overwrite(era, name, quality, quantity, owner):
    cursor = db.cursor()
    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE Relic SET Quantity = ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (quantity, name, era, quality, relic_owner,))
    else:
        cursor.execute('''INSERT INTO Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (?,?,?,?,?)''', (era, name, quality, quantity, relic_owner))
    db.commit()


def relic_owner_clear(owner):
    cursor = db.cursor()
    relic_owner = check_user_exist(owner)
    cursor.execute('''DELETE FROM Relic WHERE IDOwner = ?''', (relic_owner,))
    db.commit()
    return 'Toutes tes reliques ont étés supprimées.'
    
##############################################################################################################
#Scrapper part#


def write_relic(r_era, r_name, r_reward_c1, r_reward_c2, r_reward_c3, r_reward_u1, r_reward_u2, r_reward_r1):
    cursor = db.cursor()
    cursor.execute('''SELECT IDRelicData FROM RelicData WHERE Era = ? AND Name = ?''', (r_era, r_name,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE RelicData SET c_1 = ?, c_2 = ?, c_3 = ?, u_1 = ?, u_2 = ?, r_1 = ? WHERE Name = ? AND Era = ?''', (r_reward_c1, r_reward_c2, r_reward_c3, r_reward_u1, r_reward_u2, r_reward_r1, r_name, r_era,))
    else:
        cursor.execute('''INSERT INTO RelicData (Era, Name, c_1, c_2, c_3, u_1, u_2, r_1) VALUES (?,?,?,?,?,?,?,?)''', (r_era, r_name, r_reward_c1, r_reward_c2, r_reward_c3, r_reward_u1, r_reward_u2, r_reward_r1,))
    db.commit()


def write_part(item_name, plat_price, ducats_price):
    cursor = db.cursor()
    cursor.execute('''SELECT IDPrimePart FROM PrimePartData WHERE Name = ?''', (item_name,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE PrimePartData SET PricePlat = ?, PriceDucats = ? WHERE Name = ?''', (plat_price, ducats_price, item_name,))
    else:
        cursor.execute('''INSERT INTO PrimePartData (Name, PricePlat, PriceDucats) VALUES (?,?,?)''', (item_name, plat_price, ducats_price,))
    db.commit()
