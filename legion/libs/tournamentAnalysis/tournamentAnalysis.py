import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import dataAccess.api as api

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

def main():
    print(calculate_faction_win_rate("star-wars-legion-wq-at-pax-unplugged-2023", True, None))
    # tournament_lists_analysis("star-wars-legion-wq-at-pax-unplugged-2023")
    
if __name__ == '__main__':
    main()