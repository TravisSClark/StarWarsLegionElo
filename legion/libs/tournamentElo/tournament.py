# external
import json

# internal
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from dataAccess import api, eloDb
from util import elo

def update_tournament_data(name):
    tournament_data = api.get_tournament_data(name)
    groups = tournament_data["groups"]
    tournament_date = tournament_data["endsAt"]
    player_elo_dict, player_list, new_player_list = get_tournament_players(groups)
    if len(new_player_list) > 0:
        db_new_player_dict, db_new_player_list = insert_new_players(new_player_list, tournament_date)
        player_elo_dict.update(db_new_player_dict)
        player_list.extend(db_new_player_list)
    for group in groups:
        for round in group["rounds"]:
            for match in round["matches"]:
                if not match["isBye"] and match["winner"]:
                    player_one_id = int(match["playerOne"]["user"]["id"])
                    player_two_id = int(match["playerTwo"]["user"]["id"])
                    winner_id = int(match["winner"]["user"]["id"])
                    player_one_winner = player_one_id == winner_id
                    player_elo_dict[player_one_id]["elo"], player_elo_dict[player_two_id]["elo"] = elo.elo_rating(
                        player_elo_dict[player_one_id]["elo"], player_elo_dict[player_two_id]["elo"], player_one_winner)
                    player_elo_dict[player_one_id]["weighted_elo"], player_elo_dict[player_two_id]["weighted_elo"] = elo.weighted_elo_rating(
                        player_elo_dict[player_one_id]["weighted_elo"], player_elo_dict[player_two_id]["weighted_elo"], player_one_winner)
    # Fix this, idk
    for player in player_list:
        player["elo"] = player_id_elo_dict[player["id"]]
        player["weighted_elo"] = player_id_weighted_elo_dict[player["id"]]
        tournament_list = json.loads(player["tournaments"])
        if name not in tournament_list:
            tournament_list.append(name)
        player["tournaments"] = json.dumps(tournament_list)
        # This costs too much
        eloDb.update_player(player)
        
def get_tournament_players(groups):
    player_list, new_player_list = []
    player_id_elo_dict = {}
    for group in groups:
        for player in group["groupPlayerResults"]:
            if (not int(player["player"]["user"]["id"]) in player_id_elo_dict) and (not player in player_list):
                db_player = eloDb.get_player_info(int(player["player"]["user"]["id"])) or {}
                if not db_player:
                    new_player_list.append(player)
                else:
                    db_player["name"] = player["user"]["name"]
                    player_list.append(db_player)
                    player_id_elo_dict[db_player["id"]]["name"] = player["user"]["name"]
                    player_id_elo_dict[db_player["id"]]["elo"] = db_player["elo"]
                    player_id_elo_dict[db_player["id"]]["weighted_elo"] = db_player["weighted_elo"]
    return player_id_elo_dict, player_list, new_player_list

def insert_new_players(new_player_list, tournament_date):
    player_list = []
    player_id_elo_dict = {}
    for player in new_player_list:
        eloDb.insert_player(player["user"]["id"], player["user"]["name"], tournament_date)
        db_player = eloDb.get_player_info(int(player["user"]["id"]))
        player_id_elo_dict[db_player["id"]]["name"] = player["user"]["name"]
        player_id_elo_dict[db_player["id"]]["elo"] = db_player["elo"]
        player_id_elo_dict[db_player["id"]]["weighted_elo"] = db_player["weighted_elo"]
    return player_list, player_id_elo_dict
    
def get_game_results(db_player, player):
    db_player["games"] += player["wonMatchesAmount"] + player["lostMatchesAmount"]
    db_player["wins"] += player["wonMatchesAmount"]
    db_player["loses"] += player["lostMatchesAmount"]
    if player["player"]["legionList"]:
        match player["player"]["legionList"]["faction"]:
            case "EMPIRE":
                db_player["empire_wins"] += player["wonMatchesAmount"]
                db_player["empire_loses"] += player["lostMatchesAmount"]
            case "REBELS":
                db_player["rebels_wins"] += player["wonMatchesAmount"]
                db_player["rebels_loses"] += player["lostMatchesAmount"]
            case "REPUBLIC":
                db_player["republic_wins"] += player["wonMatchesAmount"]
                db_player["republic_loses"] += player["lostMatchesAmount"]
            case "SEPARATISTS":
                db_player["separatists_wins"] += player["wonMatchesAmount"]
                db_player["separatists_loses"] += player["lostMatchesAmount"]
            case "MERCENARY":
                db_player["mercenary_wins"] += player["wonMatchesAmount"]
                db_player["mercenary_loses"] += player["lostMatchesAmount"]
    return db_player

def get_elo_of_tournament_players(name, groups):
    if groups is None:
        groups = api.get_tournament_data(name)["groups"]
    player_id_elo_dict, _, _ = get_tournament_players(groups)
    return player_id_elo_dict

def main():
    # update_tournament_data("star-wars-legion-wq-at-pax-unplugged-2023")
    # update_tournament_data("atomic-empire-star-wars-legion-tournament-darkness-descends")
    player_list = get_elo_of_tournament_players("cherokee-open-2024", None)
    sorted_player_list = sorted(player_list, key=lambda i: i["elo"], reverse=True)
    print(sorted_player_list)
    
if __name__ == '__main__':
    main()