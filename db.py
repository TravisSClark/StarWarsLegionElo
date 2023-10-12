import sqlite3
from sqlite3 import Error

tableName = "players"
defaultElo = 800

def create_connection():
    database = r'sqlite\db\eloSQLite.db'
    conn = None
    
    try:
        conn = sqlite3.connect(database)
        return conn
    except Error as e:
        print(e)
        
    return conn

def create_table():
    conn = create_connection()
    
    if conn is not None:
        sql_create_players_table = f""" CREATE TABLE {tableName} (
                                            id integer PRIMARY KEY,
                                            name text NOT NULL,
                                            elo integer DEFAULT {defaultElo}
                                        ); """
        try:
            cur = conn.cursor()
            cur.execute(sql_create_players_table)
            cur.close()
        except Error as e:
            print(e)
        conn.close()
    else:
        print("Error! Cannot create table.")
        
def get_all():
    conn = create_connection()
    
    if conn is not None:
        sql_select_player = f"SELECT * FROM {tableName}"
        cur = conn.cursor()
        cur.execute(sql_select_player)
        players = cur.fetchall()
        players.sort(key = lambda i:i[2], reverse = True)
        players = [dict(zip([c[0] for c in cur.description], player)) for player in players]
        cur.close()
        conn.close()
        return players
    else:
        print("Error! Cannot get all players.")
        
def get_player(id):
    conn = create_connection()
    
    if conn is not None:
        sql_select_player = f"SELECT * FROM {tableName} WHERE id={id}"
        cur = conn.cursor()
        cur.execute(sql_select_player)
        player = cur.fetchone()
        if player != None:
            player = dict(zip([c[0] for c in cur.description], player))
        cur.close()
        conn.close()
        return player
    else:
        print("Error! Cannot get player.")

def insert_player(id, name):
    conn = create_connection()
    
    if conn is not None:
        sql_insert_player = f"INSERT INTO {tableName}(id, name) VALUES(?,?)"
        cur = conn.cursor()
        cur.execute(sql_insert_player, (id, name))
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("Error! Cannot insert new player.")
    
def update_player(id, name, elo):
    conn = create_connection()
    
    if conn is not None:
        sql_update_player = f" UPDATE {tableName} SET name = ? , elo = ? WHERE id = ?"
        cur = conn.cursor()
        cur.execute(sql_update_player, (name, elo, id))
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("Error! Cannot update player.")
    
# create_table()
# insert_player(0, "Test")
    
def main():
    create_table()
#     print(get_player(0))
#     print(get_all())
        
    
if __name__ == '__main__':
    main()