import dao
import db

class Person:
  def __init__(self, id, name, elo):
    self.id = id
    self.name = name
    self.elo = elo

def get_tournament_data(name):
    groups = dao.get_tournament_groups(name)
    for group in groups:
        players = []
        for player in group["players"]:
            player_info= player["user"]
            players.append(get_player_info(player_info))

def get_player_info(player_info):
    db_player = db.get_player(int(player_info["id"]))
    #db_player = db.get_player(3)
    if db_player == None:
        return Person(player_info["id"], player_info["name"], db.defaultElo)
    else:
        return Person(*db_player)