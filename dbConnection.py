import sqlite3
from sqlite3 import Error

tableName = "players"
defaultElo = 800
defaultGames = 0

def create_connection():
    database = r'D:\Projects\sqlite\db\eloSQLite.db'
    conn = None
    
    try:
        conn = sqlite3.connect(database)
        return conn
    except Error as e:
        print(e)
        
    return conn

def create_table(conn):
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
    
    
def main():
    #if player == None:
    #    insert_player(conn, 3, "Billy")
    #    player = get_player(conn, 3)
    players = get_all()
    print(players)
        
    
if __name__ == '__main__':
    main()