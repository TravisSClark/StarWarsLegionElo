# external
import sqlite3
from sqlite3 import Error

playerStatsTableName = "Player_Stats"
defaultGames = 0

def create_connection():
    database = r'..\sqlite\db\statsSQLite.db'
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
        sql_create_players_table = f""" CREATE TABLE {playerStatsTableName} (
                                            id integer PRIMARY KEY,
                                            empire_wins integar DEFAULT {defaultGames},
                                            empire_loses integar DEFAULT {defaultGames},
                                            rebels_wins integar DEFAULT {defaultGames},
                                            rebels_loses integar DEFAULT {defaultGames},
                                            republic_wins integar DEFAULT {defaultGames},
                                            republic_loses integar DEFAULT {defaultGames},
                                            separatists_wins integar DEFAULT {defaultGames},
                                            separatists_loses integar DEFAULT {defaultGames},
                                            mercenary_wins integar DEFAULT {defaultGames},
                                            mercenary_loses integar DEFAULT {defaultGames},
                                            tournaments text DEFAULT '[]'
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
        sql_select_player = f"""SELECT * FROM {playerStatsTableName}"""
        cur = conn.cursor()
        cur.execute(sql_select_player)
        columns = cur.description 
        players = [{columns[index][0]:column for index, column in enumerate(value)} for value in cur.fetchall()]

        cur.close()
        conn.close()
        return players
    else:
        print("Error! Cannot get all players.")
        
def get_player(id):
    conn = create_connection(playerStatsTableName)
    
    if conn is not None:
        sql_select_player = f"SELECT * FROM {playerStatsTableName} WHERE id={id}"
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
    conn = create_connection(playerStatsTableName)
    
    if conn is not None:
        sql_insert_player = f"INSERT INTO {playerStatsTableName} (id, name) VALUES(?,?)"
        cur = conn.cursor()
        cur.execute(sql_insert_player, (id, name))
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("Error! Cannot insert new player.")
    
def update_player(player):
    conn = create_connection(playerStatsTableName)
    
    if conn is not None:
        sql_update_player = f""" UPDATE {playerStatsTableName} SET empire_wins = ? , empire_loses = ? , rebels_wins = ? , rebels_loses = ? , 
        republic_wins = ? , republic_loses = ? , separatists_wins = ? , separatists_loses = ? , mercenary_wins = ? , mercenary_loses = ? , tournaments = ? 
        WHERE id = ?"""
        cur = conn.cursor()
        cur.execute(sql_update_player, (player["empire_wins"], player["empire_loses"], player["rebels_wins"], player["rebels_loses"],
                                        player["republic_wins"], player["republic_loses"], player["separatists_wins"], player["separatists_loses"],
                                        player["mercenary_wins"], player["mercenary_loses"], player["tournaments"], player["id"]))
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("Error! Cannot update player.")
    
def main():
    create_table()
    
if __name__ == '__main__':
    main()