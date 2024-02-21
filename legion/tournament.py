# external
import json

# internal
import dataAccess.api as api
import dataAccess.db as db
import util.elo as elo

def get_elo_of_tournament_players(name, groups):
    if groups is None:
        groups = api.get_tournament_data(name)
    total_player_list = []
    for group in groups:
        player_list, _, _ = get_tournament_player_list(group["groupPlayerResults"])
        total_player_list.extend(player_list)
    return total_player_list

def calculate_faction_win_rate(name, include_mirrored, groups):
    faction_win_dict = {"EMPIRE" : {"Wins" : 0, "Loses" : 0, "Winrate" : 0.0}, \
        "REBELS" : {"Wins" : 0, "Loses" : 0, "Winrate" : 0.0}, \
        "REPUBLIC" : {"Wins" : 0, "Loses" : 0, "Winrate" : 0.0}, \
        "SEPARATISTS" : {"Wins" : 0, "Loses" : 0, "Winrate" : 0.0}, \
        "MERCENARY" : {"Wins" : 0, "Loses" : 0, "Winrate" : 0.0}}
    player_id_faction_dict = {}
    
    if groups is None:
        groups = api.get_tournament_data(name)
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
                        if winner_id in player_id_faction_dict and loser_id in player_id_faction_dict:
                            if include_mirrored or player_id_faction_dict[winner_id] != player_id_faction_dict[loser_id]:
                                faction_win_dict[player_id_faction_dict[winner_id]]["Wins"] += 1
                                faction_win_dict[player_id_faction_dict[loser_id]]["Loses"] += 1
                     
    for faction in faction_win_dict:
        faction_win_dict[faction]["Winrate"] = 100 * faction_win_dict[faction]["Wins"] / (faction_win_dict[faction]["Wins"] + faction_win_dict[faction]["Loses"])
    return dict(sorted(faction_win_dict.items(), key=lambda item: item[1]["Winrate"], reverse=True))

def tournament_lists_analysis(name):
    tournament_lists = get_tournament_lists(name)
    objective_card_dict = deployment_card_dict = condition_card_dict = command_card_dict = units_dict = upgrades_card_dict = {}
    for list in tournament_lists:
        battlefield_cards = list["battlefieldCards"]
        if len(battlefield_cards) > 0:
            for bcard in battlefield_cards:
                match bcard["card"]["subType"]:
                    case "objective":
                        if bcard["card"]["name"] in objective_card_dict:
                            objective_card_dict[bcard["card"]["name"]] += 1
                        else:
                            objective_card_dict[bcard["card"]["name"]] = 1
                    case "deployment":
                        if bcard["card"]["name"] in deployment_card_dict:
                            deployment_card_dict[bcard["card"]["name"]] += 1
                        else:
                            deployment_card_dict[bcard["card"]["name"]] = 1
                    case "condition":
                        if bcard["card"]["name"] in condition_card_dict:
                            condition_card_dict[bcard["card"]["name"]] += 1
                        else:
                            condition_card_dict[bcard["card"]["name"]] = 1
    print(objective_card_dict, deployment_card_dict, condition_card_dict)

def get_tournament_lists(name):
    groups = api.get_tournament_data(name)
    player_id_list = []
    for group in groups:
        for player in group["players"]:
            player_id_list.append(player["id"])
    print(player_id_list)
    api_list_data = api.get_tournament_lists(player_id_list)
    return api_list_data.json()["data"]["legionLists"]

def update_tournament_data(name):
    groups = api.get_tournament_data(name)
    if groups:
        for group in groups:
            player_list, player_id_elo_dict, player_id_weighted_elo_dict = get_tournament_player_list(group["groupPlayerResults"])
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

def get_tournament_player_list(players):
    player_list = []
    player_id_elo_dict = player_id_weighted_elo_dict = {}
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
    db_player["elo"] = db_player["weighted_elo"] = db.defaultElo
    db_player["games"] = db_player["wins"] = db_player["loses"] = \
        db_player["empire_wins"] = db_player["empire_loses"] = \
        db_player["rebels_wins"] = db_player["rebels_loses"] = \
        db_player["republic_wins"] = db_player["republic_loses"] = \
        db_player["separatists_wins"] = db_player["separatists_loses"] = \
        db_player["mercenary_wins"] = db_player["mercenary_loses"] = 0
    db_player["tournaments"] ="[]"
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
    # player_list = get_elo_of_tournament_players("star-wars-legion-wq-at-pax-unplugged-2023", None)
    # sorted_player_list = sorted(player_list, key=lambda i: i["weighted_elo"], reverse=True)
    # print(sorted_player_list)
    
    print(calculate_faction_win_rate("star-wars-legion-wq-at-pax-unplugged-2023", True, None))
    # tournament_lists_analysis("star-wars-legion-wq-at-pax-unplugged-2023")
    
if __name__ == '__main__':
    main()