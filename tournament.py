# external
import json
import cProfile
import re

# internal
import db
import elo
import service

def get_elo_of_tournament_players(name):
    groups = service.get_tournament_groups(name)
    total_player_list = []
    for group in groups:
        player_list, _, _ = get_player_list(group["groupPlayerResults"])
        total_player_list.extend(player_list)
    return total_player_list

def update_tournament_data(name):
    groups = service.get_tournament_groups(name)
    if groups:
        for group in groups:
            player_list, player_id_elo_dict, player_id_weighted_elo_dict = get_player_list(group["groupPlayerResults"])
            for round in group["rounds"]:
                for match in round["matches"]:
                    if not match["isBye"] and match["winner"]:
                        player_one_id = int(match["playerOne"]["user"]["id"])
                        player_two_id = int(match["playerTwo"]["user"]["id"])
                        winner_id = int(match["winner"]["user"]["id"])
                        player_one_winner = player_one_id == winner_id
                        player_id_elo_dict[player_one_id], player_id_elo_dict[player_two_id] = elo.elo_rating(
                            player_id_elo_dict[player_one_id], player_id_elo_dict[player_two_id], player_one_winner)
                        player_id_weighted_elo_dict[player_one_id], player_id_weighted_elo_dict[player_two_id] = elo.weighted_elo_rating(
                            player_id_weighted_elo_dict[player_one_id], player_id_weighted_elo_dict[player_two_id], player_one_winner)
            for player in player_list:
                player["elo"] = player_id_elo_dict[player["id"]]
                player["weighted_elo"] = player_id_weighted_elo_dict[player["id"]]
                tournament_list = json.loads(player["tournaments"])
                if name not in tournament_list:
                    tournament_list.append(name)
                player["tournaments"] = json.dumps(tournament_list)
                # This costs too much
                db.update_player(player)

def get_player_list(players):
    player_list = []
    player_id_elo_dict = {}
    player_id_weighted_elo_dict = {}
    for player in players:
        db_player = get_player_info_from_db(player["player"])
        updated_player = get_game_results(db_player, player)
        player_list.append(updated_player)
        player_id_elo_dict[updated_player["id"]] = updated_player["elo"]
        player_id_weighted_elo_dict[updated_player["id"]] = updated_player["weighted_elo"]
    
    return player_list, player_id_elo_dict, player_id_weighted_elo_dict

def get_player_info_from_db(player):
    db_player = db.get_player(int(player["user"]["id"])) or {}
    if not db_player:
        db.insert_player(player["user"]["id"], player["user"]["name"])
        db_player["id"] = int(player["user"]["id"])
        db_player = set_default_player(db_player)
    db_player["name"] = player["user"]["name"]
    return db_player

def set_default_player(db_player):
    db_player["elo"] = db.defaultElo
    db_player["weighted_elo"] = db.defaultElo
    db_player["games"] = 0
    db_player["wins"] = 0
    db_player["loses"] = 0
    db_player["empire_wins"] = 0
    db_player["empire_loses"] = 0
    db_player["rebels_wins"] = 0
    db_player["rebels_loses"] = 0
    db_player["republic_wins"] = 0
    db_player["republic_loses"] = 0
    db_player["separatists_wins"] = 0
    db_player["separatists_loses"] = 0
    db_player["mercenary_wins"] = 0
    db_player["mercenary_loses"] = 0
    db_player["tournaments"] = "[]"
    return db_player
    
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

def main():
    #  update_tournament_data("las-vegas-open-grand-championship")
    # update_tournament_data("atomic-empire-star-wars-legion-tournament-darkness-descends")
    player_list = get_elo_of_tournament_players("las-vegas-open-grand-championship")
    sorted_player_list = sorted(player_list, key=lambda i: i["weighted_elo"], reverse=True)
    print(sorted_player_list)
    
if __name__ == '__main__':
    # cProfile.run('main()')
    main()