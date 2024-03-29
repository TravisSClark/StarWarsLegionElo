# external
import sqlite3
from sqlite3 import Error

playerEloTableName = "Player_Elos"
defaultElo = 800
defaultGames = 0

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
        sql_create_players_table = f""" CREATE TABLE {playerEloTableName} (
                                            id integer PRIMARY KEY,
                                            name text NOT NULL,
                                            elo integer DEFAULT {defaultElo},
                                            weighted_elo integer DEFAULT {defaultElo},
                                            games integer DEFAULT {defaultGames},
                                            wins integer DEFAULT {defaultGames},
                                            loses integer DEFAULT {defaultGames},
                                            change integer DEFAULT {defaultGames},
                                            change_date integer NOT NULL,
                                            bonus_points integer DEFAULT {defaultGames}
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
    return get_all_sorted("elo")
    
def get_all_sorted(sort_column):
    conn = create_connection()
    
    if conn is not None:
        sql_select_player = f"""SELECT ROW_NUMBER () OVER ( ORDER BY {sort_column} DESC, elo DESC ) RowNum, name, elo, weighted_elo, games, wins, loses,
            change, change_date, bonus_points FROM {playerEloTableName}"""
        cur = conn.cursor()
        cur.execute(sql_select_player)
        columns = cur.description 
        players = [{columns[index][0]:column for index, column in enumerate(value)} for value in cur.fetchall()]

        cur.close()
        conn.close()
        return players
    else:
        print("Error! Cannot get all players.")
        
def get_player_info(id):
    conn = create_connection()
    
    if conn is not None:
        sql_select_player = f"SELECT * FROM {playerEloTableName} WHERE id={id}"
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

def get_players_not_played_since_date(date):
    conn = create_connection()
    
    if conn is not None:
        sql_select_players = f"SELECT * FROM {playerEloTableName} WHERE change_date<{date}"
        cur = conn.cursor()
        cur.execute(sql_select_players)
        columns = cur.description 
        players = [{columns[index][0]:column for index, column in enumerate(value)} for value in cur.fetchall()]
        cur.close()
        conn.close()
        return players
    else:
        print("Error! Cannot get player.")

def insert_player(id, name, date):
    conn = create_connection()
    
    if conn is not None:
        sql_insert_player = f"INSERT INTO {playerEloTableName} (id, name, change_date) VALUES(?,?,?)"
        cur = conn.cursor()
        cur.execute(sql_insert_player, (id, name, date))
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("Error! Cannot insert new player.")
    
def update_player(player):
    conn = create_connection()
    
    if conn is not None:
        sql_update_player = f""" UPDATE {playerEloTableName} SET name = ? , elo = ? , weighted_elo = ? ,games = ? , wins = ? , loses = ? , change = ? , change_date = ?, bonus_points = ?
        WHERE id = ?"""
        cur = conn.cursor()
        cur.execute(sql_update_player, (player["name"], player["elo"], player["weighted_elo"], player["games"], player["wins"], player["loses"], player["change"], player["change_date"], player["bonus_points"], player["id"]))
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("Error! Cannot update player.")
        
def bulk_update_players(players):
    conn = create_connection()
    
    if conn is not None:
        sql_update_player = f""" UPDATE {playerEloTableName} SET name = ? , elo = ? , weighted_elo = ? , games = ? , wins = ? , loses = ? , change = ? , change_date = ?, bonus_points = ?
        WHERE id = ?"""
        cur = conn.cursor()
        cur.executemany(sql_update_player, [(player["name"], player["elo"], player["weighted_elo"], player["games"], player["wins"], player["loses"], player["change"], player["change_date"], player["bonus_points"], player["id"]) for player in players])
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("Error! Cannot update player.")
    
def main():
    create_table()
    # print(get_players_not_played_since_date(20231230))
    
if __name__ == '__main__':
    main()