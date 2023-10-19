# external
from pprint import pprint

# internal
import db
import elo
import service

def update_tournament_data(name):
    groups = service.get_tournament_groups(name)
    for group in groups:
        player_list, player_id_elo_dict = get_player_list(group["groupPlayerResults"])
        for round in group["rounds"]:
            for match in round["matches"]:
                if not match["isBye"] and match["winner"]:
                    player_one_id = int(match["playerOne"]["user"]["id"])
                    player_two_id = int(match["playerTwo"]["user"]["id"])
                    winner_id = int(match["winner"]["user"]["id"])
                    player_one_winner = player_one_id == winner_id
                    player_id_elo_dict[player_one_id], player_id_elo_dict[player_two_id] = elo.elo_rating(
                        player_id_elo_dict[player_one_id], player_id_elo_dict[player_two_id], player_one_winner)
        for player in player_list:
            player["elo"] = player_id_elo_dict[player["id"]]
            db.update_player(player)
                
def get_elo_of_tournament_players(name):
    groups = service.get_tournament_groups(name)
    total_player_list = []
    for group in groups:
        player_list, _ = get_player_list(group["groupPlayerResults"])
        total_player_list.extend(player_list)
    return total_player_list

def get_player_list(players):
    player_list = []
    player_id_elo_dict = {}
    for player in players:
        db_player = get_player_info_from_db(player["player"])
        updated_player = get_game_results(db_player, player)
        player_list.append(updated_player)
        player_id_elo_dict[updated_player["id"]] = updated_player["elo"]
    
    return player_list, player_id_elo_dict

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
    # update_tournament_data("las-vegas-open-grand-championship")
    update_tournament_data("atomic-empire-star-wars-legion-tournament-darkness-descends")
    player_list = get_elo_of_tournament_players("atomic-empire-star-wars-legion-tournament-darkness-descends")
    sorted_player_list = sorted(player_list, key=lambda i: i["elo"], reverse=True)
    print(sorted_player_list)
    
if __name__ == '__main__':
    main()