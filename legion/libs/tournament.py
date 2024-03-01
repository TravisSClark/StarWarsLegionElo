# external
import json
import sys
import os
from datetime import datetime

# internal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dataAccess import api, eloDb
from util import elo

def update_tournament_data(name):
    tournament_data = api.get_tournament_data(name)
    groups = tournament_data["groups"]
    tournament_date = tournament_data["endsAt"]
    date_format = '%Y-%m-%d %H:%M:%S'
    new_date_format = '%Y%m%d'
    change_date = int(datetime.strptime(tournament_date, date_format).strftime(new_date_format))
    player_elo_dict, player_list, new_player_list = get_tournament_players(groups)
    # Retry logic basically
    if len(new_player_list) > 0:
        db_new_player_dict, db_new_player_list = insert_new_players(new_player_list, change_date)
        player_elo_dict.update(db_new_player_dict)
        player_list.extend(db_new_player_list)
    for group in groups:
        # Wins, Loses, and Factions are all set in the groupPlayerResults part of the group
        player_elo_dict = get_game_results(player_elo_dict, group["groupPlayerResults"])
        for round in group["rounds"]:
            for match in round["matches"]:
                if not match["isBye"] and match["winner"]:
                    player_one_id = int(match["playerOne"]["user"]["id"])
                    player_two_id = int(match["playerTwo"]["user"]["id"])
                    winner_id = int(match["winner"]["user"]["id"])
                    player_one_winner = player_one_id == winner_id
                    player_elo_dict[player_one_id]["elo"], player_elo_dict[player_two_id]["elo"] = elo.elo_rating(
                        player_elo_dict[player_one_id]["elo"], player_elo_dict[player_two_id]["elo"], player_one_winner)
                    player_elo_dict[player_one_id]["weighted_elo"], player_elo_dict[player_two_id]["weighted_elo"], \
                        player_elo_dict[player_one_id]["bonus_points"], player_elo_dict[player_two_id]["bonus_points"] = elo.weighted_elo_rating(
                            player_elo_dict[player_one_id]["weighted_elo"], player_elo_dict[player_two_id]["weighted_elo"], player_one_winner,
                            player_elo_dict[player_one_id]["games"],  player_elo_dict[player_one_id]["bonus_points"],
                            player_elo_dict[player_one_id]["games"], player_elo_dict[player_two_id]["bonus_points"])
                    player_elo_dict[player_one_id]["games"] += 1
                    player_elo_dict[player_two_id]["games"] += 1
    for player in player_list:
        player["elo"] = player_elo_dict[player["id"]]["elo"]
        player["change"] = player_elo_dict[player["id"]]["weighted_elo"] - player_elo_dict[player["id"]]["starting_elo"]
        player["change_date"] = change_date
        player["weighted_elo"] = player_elo_dict[player["id"]]["weighted_elo"]
        player["games"] = player_elo_dict[player["id"]]["games"]
        player["wins"] = player_elo_dict[player["id"]]["wins"]
        player["loses"] = player_elo_dict[player["id"]]["loses"]
        player["bonus_points"] = player_elo_dict[player["id"]]["bonus_points"]
        # tournament_list = json.loads(player["tournaments"])
        # tournament_list.append(name)
        # player["tournaments"] = json.dumps(tournament_list)
    eloDb.bulk_update_players(player_list)
    # only for initial runs
    return player_list, tournament_date
        
def get_tournament_players(groups):
    player_list = []
    new_player_list = []
    player_id_elo_dict = {}
    for group in groups:
        for player in group["groupPlayerResults"]:
            if (not int(player["player"]["user"]["id"]) in player_id_elo_dict) and (not player["player"]["user"] in new_player_list):
                db_player = eloDb.get_player_info(int(player["player"]["user"]["id"])) or {}
                if not db_player:
                    new_player_list.append(player["player"]["user"])
                else:
                    db_player["name"] = player["player"]["user"]["name"]
                    player_id_elo_dict, player_list = initialize_elo_dict_and_list(player, db_player, player_id_elo_dict, player_list)
    return player_id_elo_dict, player_list, new_player_list

# Could probably remove duplicate codde from get tournament_players
def insert_new_players(new_player_list, tournament_date):
    player_list = []
    player_id_elo_dict = {}
    for player in new_player_list:
        eloDb.insert_player(player["id"], player["name"], tournament_date)
        db_player = eloDb.get_player_info(int(player["id"]))
        player_id_elo_dict, player_list = initialize_elo_dict_and_list(player, db_player, player_id_elo_dict, player_list)
    return player_id_elo_dict, player_list

def initialize_elo_dict_and_list(player, db_player, player_id_elo_dict, player_list):
    player_list.append(db_player)
    player_id_elo_dict[db_player["id"]] = {}
    player_id_elo_dict[db_player["id"]]["name"] = db_player["name"]
    player_id_elo_dict[db_player["id"]]["elo"] = db_player["elo"]
    player_id_elo_dict[db_player["id"]]["weighted_elo"] = db_player["weighted_elo"]
    player_id_elo_dict[db_player["id"]]["starting_elo"] = db_player["weighted_elo"]
    player_id_elo_dict[db_player["id"]]["games"] = db_player["games"]
    player_id_elo_dict[db_player["id"]]["wins"] = db_player["wins"]
    player_id_elo_dict[db_player["id"]]["loses"] = db_player["loses"]
    player_id_elo_dict[db_player["id"]]["bonus_points"] = db_player["bonus_points"]
    return player_id_elo_dict, player_list
    
def get_game_results(player_elo_dict, players):
    for player in players:
        player_id = int(player["player"]["user"]["id"])
        player_elo_dict[player_id]["wins"] += player["wonMatchesAmount"]
        player_elo_dict[player_id]["loses"] += player["lostMatchesAmount"]
        # if player["player"]["legionList"]:
        #     match player["player"]["legionList"]["faction"]:
        #         case "EMPIRE":
        #             db_player["empire_wins"] += player["wonMatchesAmount"]
        #             db_player["empire_loses"] += player["lostMatchesAmount"]
        #         case "REBELS":
        #             db_player["rebels_wins"] += player["wonMatchesAmount"]
        #             db_player["rebels_loses"] += player["lostMatchesAmount"]
        #         case "REPUBLIC":
        #             db_player["republic_wins"] += player["wonMatchesAmount"]
        #             db_player["republic_loses"] += player["lostMatchesAmount"]
        #         case "SEPARATISTS":
        #             db_player["separatists_wins"] += player["wonMatchesAmount"]
        #             db_player["separatists_loses"] += player["lostMatchesAmount"]
        #         case "MERCENARY":
        #             db_player["mercenary_wins"] += player["wonMatchesAmount"]
        #             db_player["mercenary_loses"] += player["lostMatchesAmount"]
    return player_elo_dict

def get_elo_of_tournament_players(name):
    groups = api.get_tournament_data(name)["groups"]
    _, player_list, _ = get_tournament_players(groups)
    return player_list, groups

def main():
    # update_tournament_data("star-wars-legion-wq-at-pax-unplugged-2023")
    update_tournament_data("atomic-empire-star-wars-legion-tournament-darkness-descends")
    update_tournament_data("cherokee-open-2024")
    player_list, _ = get_elo_of_tournament_players("atomic-empire-star-wars-legion-tournament-darkness-descends", None)
    sorted_player_list = sorted(player_list, key=lambda i: i["elo"], reverse=True)
    print(sorted_player_list)
    
if __name__ == '__main__':
    main()