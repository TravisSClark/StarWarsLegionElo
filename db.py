# external
import sqlite3
from sqlite3 import Error

tableName = "players"
defaultElo = 800

def create_connection():
    database = r'..\sqlite\db\eloSQLite.db'
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
                                            elo integer DEFAULT {defaultElo},
                                            games integer DEFAULT 0,
                                            wins integer DEFAULT 0,
                                            loses integer DEFAULT 0,
                                            empire_wins integar DEFAULT 0,
                                            empire_loses integar DEFAULT 0,
                                            rebels_wins integar DEFAULT 0,
                                            rebels_loses integar DEFAULT 0,
                                            republic_wins integar DEFAULT 0,
                                            republic_loses integar DEFAULT 0,
                                            separatists_wins integar DEFAULT 0,
                                            separatists_loses integar DEFAULT 0,
                                            mercenary_wins integar DEFAULT 0,
                                            mercenary_loses integar DEFAULT 0
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
        sql_select_player = f"SELECT ROW_NUMBER () OVER ( ORDER BY elo DESC ) RowNum, name, elo FROM {tableName}"
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
        sql_insert_player = f"INSERT INTO {tableName} (id, name) VALUES(?,?)"
        cur = conn.cursor()
        cur.execute(sql_insert_player, (id, name))
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("Error! Cannot insert new player.")
    
def update_player(player):
    conn = create_connection()
    
    if conn is not None:
        sql_update_player = f""" UPDATE {tableName} SET name = ? , elo = ? , games = ? , wins = ? , loses = ? , 
        empire_wins = ? , empire_loses = ? , rebels_wins = ? , rebels_loses = ? , 
        republic_wins = ? , republic_loses = ? , separatists_wins = ? , separatists_loses = ? , mercenary_wins = ? , mercenary_loses = ? 
        WHERE id = ?"""
        cur = conn.cursor()
        cur.execute(sql_update_player, (player["name"], player["elo"], player["games"], player["wins"], player["loses"],
                                        player["empire_wins"], player["empire_loses"], player["rebels_wins"], player["rebels_loses"],
                                        player["republic_wins"], player["republic_loses"], player["separatists_wins"], player["separatists_loses"],
                                        player["mercenary_wins"], player["mercenary_loses"],player["id"]))
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("Error! Cannot update player.")
    
def main():
    create_table()
    
if __name__ == '__main__':
    main()