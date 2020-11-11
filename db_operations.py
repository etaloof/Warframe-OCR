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

    cursor.execute('''SELECT IDUser FROM User WHERE Pseudo = %s''', (owner,))
    result = cursor.fetchone()

    if result:

        close_db_con(db, cursor)  # Close DB session

        return result[0]

    else:
        cursor.execute('''INSERT INTO User (Pseudo) VALUES (%s)''', (owner,))

        close_db_con(db, cursor, commit=True)  # Close DB session

        return cursor.lastrowid


# Add a relic to the DB using INSERT/UPDATE
def add_relic_to_db(era, name, quality, quantity, owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic FROM relic_Relic WHERE Name = %s AND Era = %s AND Quality = %s AND IDOwner = %s''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE relic_Relic SET Quantity = Quantity + %s WHERE Name = %s AND Era = %s AND Quality = %s AND IDOwner = %s''', (quantity, name, era, quality, relic_owner,))
    else:
        cursor.execute('''INSERT INTO relic_Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (%s, %s, %s, %s, %s)''', (era, name, quality, quantity, relic_owner))

    close_db_con(db, cursor, commit=True)  # Close DB session


# Delete a relic on the DB using UPDATE
def del_relic_on_db(era, name, quality, quantity, owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic, Quantity FROM relic_Relic WHERE Name = %s AND Era = %s AND Quality = %s AND IDOwner = %s''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if (result[1] - quantity) < 0:
        cursor.execute('''UPDATE relic_Relic SET Quantity = 0 WHERE Name = %s AND Era = %s AND Quality = %s AND IDOwner = %s''', (name, era, quality, relic_owner,))

        close_db_con(db, cursor, commit=True)  # Close DB session

        return True
    elif result:
        cursor.execute('''UPDATE relic_Relic SET Quantity = Quantity - %s WHERE Name = %s AND Era = %s AND Quality = %s AND IDOwner = %s''', (quantity, name, era, quality, relic_owner,))

        close_db_con(db, cursor, commit=True)  # Close DB session

        return True
    else:

        close_db_con(db, cursor)  # Close DB session

        return 'Tu ne peux pas supprimer une relique que tu ne possèdes pas, Tenno !'


# Refine an already owned relic
def refine_relics(era, name, quality, quantity, owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    cursor.execute('''SELECT IDRelic FROM relic_Relic WHERE Name = %s AND Era = %s AND Quality = 'Intacte' AND IDOwner = %s AND Quantity >= %s''', (name, era, relic_owner, quantity))
    result = cursor.fetchone()
    if result:
        print('La relique existe et peut être raffinnée')
        cursor.execute('''UPDATE relic_Relic SET Quantity = Quantity - %s WHERE Name = %s AND Era = %s AND Quality = 'Intacte' AND IDOwner = %s''', (quantity, name, era, relic_owner,))
        # TestQuery
        cursor.execute('''SELECT IDRelic FROM relic_Relic WHERE Name = %s AND Era = %s AND Quality = %s AND IDOwner = %s''', (name, era, quality, relic_owner,))
        result = cursor.fetchone()
        if result:
            cursor.execute('''UPDATE relic_Relic SET Quantity = Quantity + %s WHERE Name = %s AND Era = %s AND Quality = %s AND IDOwner = %s''', (quantity, name, era, quality, relic_owner,))
        else:
            cursor.execute('''INSERT INTO relic_Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (%s, %s, %s, %s, %s)''', (era, name, quality, quantity, relic_owner))

        close_db_con(db, cursor, commit=True)  # Close DB session

        return True
    else:
        return 'Tu ne peux pas raffiner une relique que tu ne possèdes pas, Tenno !'


# NOT USED Add relic from screen and update the quantity if already exist
def relic_from_screen_not_used(era, name, quality, quantity, owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic FROM relic_Relic WHERE Name = %s AND Era = %s AND Quality = %s AND IDOwner = %s''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE relic_Relic SET Quantity = Quantity + %s WHERE Name = %s AND Era = %s AND Quality = %s AND IDOwner = %s''', (quantity, name, era, quality, relic_owner,))
    else:
        cursor.execute('''INSERT INTO relic_Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (%s, %s, %s, %s, %s)''', (era, name, quality, quantity, relic_owner))

    close_db_con(db, cursor, commit=True)  # Close DB session


# Add relic from screen and overwrite the quantity if already exist
def relic_from_screen_overwrite(era, name, quality, quantity, owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    # TestQuery
    cursor.execute('''SELECT IDRelic FROM relic_Relic WHERE Name = %s AND Era = %s AND Quality = %s AND IDOwner = %s''', (name, era, quality, relic_owner,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE relic_Relic SET Quantity = %s WHERE Name = %s AND Era = %s AND Quality = %s AND IDOwner = %s''', (quantity, name, era, quality, relic_owner,))
    else:
        cursor.execute('''INSERT INTO relic_Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (%s, %s, %s, %s, %s)''', (era, name, quality, quantity, relic_owner))

    close_db_con(db, cursor, commit=True)  # Close DB session


def relic_owner_clear(owner):

    db, cursor = init_db_con()  # Init DB session

    relic_owner = check_user_exist(owner)
    cursor.execute('''DELETE FROM relic_Relic WHERE IDOwner = %s''', (relic_owner,))

    close_db_con(db, cursor, commit=True)  # Close DB session

    return 'Toutes tes reliques ont étés supprimées.'
    
##############################################################################################################
#Scrapper part#


def write_relic(r_era, r_name, r_reward_c1, r_reward_c2, r_reward_c3, r_reward_u1, r_reward_u2, r_reward_r1):

    db, cursor = init_db_con()  # Init DB session

    cursor.execute('''SELECT IDRelicData FROM relic_RelicData WHERE Era = %s AND Name = %s''', (r_era, r_name,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE relic_RelicData SET c_1 = %s, c_2 = %s, c_3 = %s, u_1 = %s, u_2 = %s, r_1 = %s WHERE Name = %s AND Era = %s''', (r_reward_c1, r_reward_c2, r_reward_c3, r_reward_u1, r_reward_u2, r_reward_r1, r_name, r_era,))
    else:
        cursor.execute('''INSERT INTO relic_RelicData (Era, Name, c_1, c_2, c_3, u_1, u_2, r_1) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (r_era, r_name, r_reward_c1, r_reward_c2, r_reward_c3, r_reward_u1, r_reward_u2, r_reward_r1,))

    close_db_con(db, cursor, commit=True)  # Close DB session


def write_part(item_name, plat_price, ducats_price):

    db, cursor = init_db_con()  # Init DB session

    cursor.execute('''SELECT IDPrimePart FROM relic_PrimePartData WHERE Name = %s''', (item_name,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''UPDATE PrimePartData SET PricePlat = %s, PriceDucats = %s WHERE Name = %s''', (plat_price, ducats_price, item_name,))
    else:
        cursor.execute('''INSERT INTO PrimePartData (Name, PricePlat, PriceDucats) VALUES (%s, %s, %s)''', (item_name, plat_price, ducats_price,))

    close_db_con(db, cursor, commit=True)  # Close DB session
