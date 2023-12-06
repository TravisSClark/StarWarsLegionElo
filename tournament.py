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

def calculate_not_match_faction_win_rate(name):
    empire_wins = 0
    empire_loses = 0
    rebels_wins = 0
    rebels_loses = 0
    republic_wins = 0
    republic_loses = 0
    separatists_wins = 0
    separatists_loses = 0
    mercenary_wins = 0
    mercenary_loses = 0
    player_id_faction_dict = {}
    
    groups = service.get_tournament_groups(name)
    if groups:
        for group in groups:
            players = group["players"]
            for player in players:
                if player["legionList"]:
                    player_id_faction_dict[int(player["id"])] = player["legionList"]["faction"]
            for round in group["rounds"]:
                for match in round["matches"]:
                    if not match["isBye"] and match["winner"]:
                        winner_id = int(match["winner"]["id"])
                        loser_id = int(match["loser"]["id"])
                        if (player_id_faction_dict[winner_id] != player_id_faction_dict[loser_id]):
                            match player_id_faction_dict[winner_id]:
                                case "EMPIRE": empire_wins += 1
                                case "REBELS": rebels_wins += 1
                                case "REPUBLIC": republic_wins += 1
                                case "SEPARATISTS": separatists_wins += 1
                                case "MERCENARY": mercenary_wins += 1
                            match player_id_faction_dict[loser_id]:
                                case "EMPIRE": empire_loses += 1
                                case "REBELS": rebels_loses += 1
                                case "REPUBLIC": republic_loses += 1
                                case "SEPARATISTS": separatists_loses += 1
                                case "MERCENARY": mercenary_loses += 1
                            
    empire_win_rate = 100 * empire_wins / (empire_wins + empire_loses)
    rebels_win_rate = 100 * rebels_wins / (rebels_wins + rebels_loses)
    republic_win_rate = 100 * republic_wins / (republic_wins + republic_loses)
    separatists_win_rate = 100 * separatists_wins / (separatists_wins + separatists_loses)
    mercenary_win_rate = 100 * mercenary_wins / (mercenary_wins + mercenary_loses)
    print(f"Empire: {empire_wins}-{empire_loses}, Rebels: {rebels_wins}-{rebels_loses}, Republic: {republic_wins}-{republic_loses}, Separatists: {separatists_wins}-{separatists_loses}, Mercenary: {mercenary_wins}-{mercenary_loses}")
    print(f"Empire: {empire_win_rate}, Rebels: {rebels_win_rate}, Republic: {republic_win_rate}, Separatists: {separatists_win_rate}, Mercenary: {mercenary_win_rate}")

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
    # update_tournament_data("star-wars-legion-wq-at-pax-unplugged-2023")
    # update_tournament_data("atomic-empire-star-wars-legion-tournament-darkness-descends")
    # player_list = get_elo_of_tournament_players("star-wars-legion-wq-at-pax-unplugged-2023")
    # sorted_player_list = sorted(player_list, key=lambda i: i["weighted_elo"], reverse=True)
    # print(sorted_player_list)
    calculate_not_match_faction_win_rate("star-wars-legion-wq-at-pax-unplugged-2023")
    
if __name__ == '__main__':
    # cProfile.run('main()')
    main()