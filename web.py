from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
from flask import Flask, render_template, request
application = Flask(__name__)

from loadconfig import db_host, db_name, db_user, db_pass

# Variable de connection a la DB
con_pool = MySQLConnectionPool(host=db_host, database=db_name, user=db_user, password=db_pass,
                                pool_name='my_pool', pool_size=30)

def processing(sql_data, cursor):
    results_f = []
    for element in sql_data:
        a, b = element[-2:]
        new_string = ' | '.join([f'{owner} ({value})' for owner, value in zip(a.split(','), b.split(','))])
        new_tup = (*element[:-2], new_string)
        new_l = list(new_tup)
        results_f.append(new_l)

    for element in results_f: # Pour chaque row
        list1 = []
        cursor.execute('''SELECT c_1, c_2, c_3, u_1, u_2, r_1 FROM relic_RelicData WHERE Era = ? AND Name = ?''', (element[1], element[0],))
        result = cursor.fetchone() #tuple
        list1.extend(result)
        for ele in result:
            cursor.execute('''SELECT PricePlat, PriceDucats FROM relic_PrimePartData WHERE Name = ?''', (ele,))
            result2 = cursor.fetchone() #tuple
            list1.extend(result2)
            
        element.extend(list1)
      
    return results_f

@application.route('/', methods=["GET", "POST"])
def index():
    db = sqlite3.connect('relicdb.sqlite3')
    cursor = db.cursor()
    
    if request.method == "POST":
        user_filter = request.form['user']
        quality_filter = request.form['quality']
        era_filter = request.form['era']
    
        if user_filter != '' and quality_filter == '' and era_filter == '': # user
            print('choice 1')
            cursor.execute('''SELECT relic_Relic.Name, relic_Relic.Era, relic_Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM relic_Relic INNER JOIN relic_User ON relic_Relic.IDOwner = relic_User.IDUser WHERE relic_User.Pseudo = ? GROUP BY relic_Relic.Name, relic_Relic.Era, relic_Relic.Quality''', (user_filter,))
            data = cursor.fetchall()  
            final_res = processing(data, cursor)
            return render_template('relic.html', data=final_res)
            
        if user_filter != '' and quality_filter != '' and era_filter == '': # user & quality
            print('choice 2')
            cursor.execute('''SELECT relic_Relic.Name, relic_Relic.Era, relic_Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM relic_Relic INNER JOIN relic_User ON relic_Relic.IDOwner = relic_User.IDUser WHERE relic_User.Pseudo = ? AND relic_Relic.Quality = ? GROUP BY relic_Relic.Name, relic_Relic.Era, relic_Relic.Quality''', (user_filter, quality_filter,))
            data = cursor.fetchall()  
            final_res = processing(data, cursor)
            return render_template('relic.html', data=final_res)
            
        if user_filter != '' and quality_filter == '' and era_filter != '': # user & era
            print('choice 3')
            cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser WHERE User.Pseudo = ? AND Relic.Era = ? GROUP BY Relic.Name, Relic.Era, Relic.Quality''', (user_filter, era_filter,))
            data = cursor.fetchall()  
            final_res = processing(data, cursor)
            return render_template('relic.html', data=final_res)
            
        if user_filter != '' and quality_filter != '' and era_filter != '': # user & quality & era
            print('choice 4')
            cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser WHERE User.Pseudo = ? AND Relic.Quality = ? AND Relic.Era = ? GROUP BY Relic.Name, Relic.Era, Relic.Quality''', (user_filter, quality_filter, era_filter,))
            data = cursor.fetchall()  
            final_res = processing(data, cursor)
            return render_template('relic.html', data=final_res)
            
        if user_filter == '' and quality_filter != '' and era_filter == '': # quality 
            print('choice 5')
            cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser WHERE Relic.Quality = ? GROUP BY Relic.Name, Relic.Era, Relic.Quality''', (quality_filter,))
            data = cursor.fetchall()  
            final_res = processing(data, cursor)
            return render_template('relic.html', data=final_res)
            
        if user_filter == '' and quality_filter != '' and era_filter != '': # quality & era 
            print('choice 6')
            cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser WHERE Relic.Quality = ? AND Relic.Era = ? GROUP BY Relic.Name, Relic.Era, Relic.Quality''', (quality_filter, era_filter,))
            data = cursor.fetchall()  
            final_res = processing(data, cursor)
            return render_template('relic.html', data=final_res)
            
        if user_filter == '' and quality_filter == '' and era_filter != '': # era 
            print('choice 7')
            cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser WHERE Relic.Era = ? GROUP BY Relic.Name, Relic.Era, Relic.Quality''', (era_filter,))
            data = cursor.fetchall()  
            final_res = processing(data, cursor)
            return render_template('relic.html', data=final_res)
            
        if user_filter == '' and quality_filter == '' and era_filter == '': # nothing
            print('choice 8')
            cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser GROUP BY Relic.Name, Relic.Era, Relic.Quality''')
            data = cursor.fetchall()
            final_res = processing(data, cursor)
            return render_template('relic.html', data=final_res)

    else: 
        print('choice 9')
        cursor.execute('''SELECT Relic.Name, Relic.Era, Relic.Quality, GROUP_CONCAT(`Pseudo`) AS Pseudo_g, GROUP_CONCAT(`Quantity`) AS Number_g FROM Relic INNER JOIN User ON Relic.IDOwner = User.IDUser GROUP BY Relic.Name, Relic.Era, Relic.Quality''')
        data = cursor.fetchall()
        final_res = processing(data, cursor)
        return render_template('relic.html', data=final_res)

    
    
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

