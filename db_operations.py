from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
from loadconfig import db_host, db_name, db_user, db_pass

# Variable de connection a la DB
con_pool = MySQLConnectionPool(host=db_host, database=db_name, user=db_user, password=db_pass,
                                pool_name='my_pool', pool_size=30)

print('[Init] Connexion a la db réussie !')

# DB_UTILS #####################################################################################################
################################################################################################################


def init_db_con():
    db = con_pool.get_connection()
    db.commit()
    cursor = db.cursor()
    return db, cursor


def close_db_con(db, cursor, commit=False):
    if commit is True:
        db.commit()
    cursor.close()
    db.close()

################################################################################################################
################################################################################################################


# Return actual quantity for a specific relic of an owner
def check_relic_quantity(era, name, quality, owner):

    db, cursor = init_db_con()  # Init DB session

    cursor.execute('''SELECT Quantity FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, check_user_exist(owner),))
    result = cursor.fetchone()

    close_db_con(db, cursor)  # Close DB session

    return result[0]


# Check if user exist in db. If not exist, create it. If exist, return his "IDUser" index
def check_user_exist(owner):

    db, cursor = init_db_con()  # Init DB session

    cursor.execute('''SELECT IDUser FROM User WHERE Pseudo = ?''', (owner,))
    result = cursor.fetchone()

    if result:

        close_db_con(db, cursor)  # Close DB session

        return result[0]

    else:
        cursor.execute('''INSERT INTO User (Pseudo) VALUES (?)''', (owner,))

        close_db_con(db, cursor, commit=True)  # Close DB session

        return cursor.lastrowid


# Add a relic to the DB using INSERT/UPDATE
def add_relic_to_db(era, name, quality, quantity, owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic FROM relic_Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE relic_Relic SET Quantity = Quantity + ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (quantity, name, era, quality, relic_owner,))
    else:
        cursor.execute('''INSERT INTO relic_Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (?,?,?,?,?)''', (era, name, quality, quantity, relic_owner))

    close_db_con(db, cursor, commit=True)  # Close DB session


# Delete a relic on the DB using UPDATE
def del_relic_on_db(era, name, quality, quantity, owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic, Quantity FROM relic_Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if (result[1] - quantity) < 0:
        cursor.execute('''UPDATE relic_Relic SET Quantity = 0 WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))

        close_db_con(db, cursor, commit=True)  # Close DB session

        return True
    elif result:
        cursor.execute('''UPDATE relic_Relic SET Quantity = Quantity - ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (quantity, name, era, quality, relic_owner,))

        close_db_con(db, cursor, commit=True)  # Close DB session

        return True
    else:

        close_db_con(db, cursor)  # Close DB session

        return 'Tu ne peux pas supprimer une relique que tu ne possèdes pas, Tenno !'


# Refine an already owned relic
def refine_relics(era, name, quality, quantity, owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    cursor.execute('''SELECT IDRelic FROM relic_Relic WHERE Name = ? AND Era = ? AND Quality = 'Intacte' AND IDOwner = ? AND Quantity >= ?''', (name, era, relic_owner, quantity))
    result = cursor.fetchone()
    if result:
        print('La relique existe et peut être raffinnée')
        cursor.execute('''UPDATE relic_Relic SET Quantity = Quantity - ? WHERE Name = ? AND Era = ? AND Quality = 'Intacte' AND IDOwner = ?''', (quantity, name, era, relic_owner,))
        # TestQuery
        cursor.execute('''SELECT IDRelic FROM relic_Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))
        result = cursor.fetchone()
        if result:
            cursor.execute('''UPDATE relic_Relic SET Quantity = Quantity + ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (quantity, name, era, quality, relic_owner,))
        else:
            cursor.execute('''INSERT INTO relic_Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (?,?,?,?,?)''', (era, name, quality, quantity, relic_owner))

        close_db_con(db, cursor, commit=True)  # Close DB session

        return True
    else:
        return 'Tu ne peux pas raffiner une relique que tu ne possèdes pas, Tenno !'


# NOT USED Add relic from screen and update the quantity if already exist
def relic_from_screen_not_used(era, name, quality, quantity, owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic FROM relic_Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE relic_Relic SET Quantity = Quantity + ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (quantity, name, era, quality, relic_owner,))
    else:
        cursor.execute('''INSERT INTO relic_Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (?,?,?,?,?)''', (era, name, quality, quantity, relic_owner))

    close_db_con(db, cursor, commit=True)  # Close DB session


# Add relic from screen and overwrite the quantity if already exist
def relic_from_screen_overwrite(era, name, quality, quantity, owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic FROM relic_Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE relic_Relic SET Quantity = ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (quantity, name, era, quality, relic_owner,))
    else:
        cursor.execute('''INSERT INTO relic_Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (?,?,?,?,?)''', (era, name, quality, quantity, relic_owner))

    close_db_con(db, cursor, commit=True)  # Close DB session


def relic_owner_clear(owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    cursor.execute('''DELETE FROM relic_Relic WHERE IDOwner = ?''', (relic_owner,))

    close_db_con(db, cursor, commit=True)  # Close DB session

    return 'Toutes tes reliques ont étés supprimées.'
    
##############################################################################################################
#Scrapper part#


def write_relic(r_era, r_name, r_reward_c1, r_reward_c2, r_reward_c3, r_reward_u1, r_reward_u2, r_reward_r1):

    db, cursor = init_db_con()  # Init DB session

    cursor.execute('''SELECT IDRelicData FROM relic_RelicData WHERE Era = ? AND Name = ?''', (r_era, r_name,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE relic_RelicData SET c_1 = ?, c_2 = ?, c_3 = ?, u_1 = ?, u_2 = ?, r_1 = ? WHERE Name = ? AND Era = ?''', (r_reward_c1, r_reward_c2, r_reward_c3, r_reward_u1, r_reward_u2, r_reward_r1, r_name, r_era,))
    else:
        cursor.execute('''INSERT INTO relic_RelicData (Era, Name, c_1, c_2, c_3, u_1, u_2, r_1) VALUES (?,?,?,?,?,?,?,?)''', (r_era, r_name, r_reward_c1, r_reward_c2, r_reward_c3, r_reward_u1, r_reward_u2, r_reward_r1,))

    close_db_con(db, cursor, commit=True)  # Close DB session


def write_part(item_name, plat_price, ducats_price):

    db, cursor = init_db_con()  # Init DB session

    cursor.execute('''SELECT IDPrimePart FROM relic_PrimePartData WHERE Name = ?''', (item_name,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE PrimePartData SET PricePlat = ?, PriceDucats = ? WHERE Name = ?''', (plat_price, ducats_price, item_name,))
    else:
        cursor.execute('''INSERT INTO PrimePartData (Name, PricePlat, PriceDucats) VALUES (?,?,?)''', (item_name, plat_price, ducats_price,))

    close_db_con(db, cursor, commit=True)  # Close DB session
