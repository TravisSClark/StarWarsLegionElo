import pprint
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
        groups = api.get_tournament_data(name)['groups']
    if groups:
        for group in groups:
            players = group["players"]
            for player in players:
                if player["legionList"]:
                    player_id_faction_dict[int(player["id"])] = player["legionList"]["faction"]
            for group_round in group["rounds"]:
                for match in group_round["matches"]:
                    if not match["isBye"] and match["winner"]:
                        winner_id = int(match["winner"]["id"])
                        loser_id = int(match["loser"]["id"])
                        if winner_id in player_id_faction_dict and loser_id in player_id_faction_dict:
                            if include_mirrored or player_id_faction_dict[winner_id] != player_id_faction_dict[loser_id]:
                                faction_win_dict[player_id_faction_dict[winner_id]]["Wins"] += 1
                                faction_win_dict[player_id_faction_dict[loser_id]]["Loses"] += 1
                     
    for faction in faction_win_dict:
        win_rate = 100 * faction_win_dict[faction]["Wins"] / (faction_win_dict[faction]["Wins"] + faction_win_dict[faction]["Loses"])
        faction_win_dict[faction]["Winrate"] = round(win_rate,2)
    return dict(sorted(faction_win_dict.items(), key=lambda item: item[1]["Winrate"], reverse=True))

def get_tournament_lists(name, groups):
    if not groups:
        groups = api.get_tournament_data(name)["groups"]
    player_id_list = []
    for group in groups:
        for player in group["players"]:
            player_id_list.append(player["id"])
    api_list_data = api.get_tournament_lists(player_id_list)
    return api_list_data.json()["data"]["legionLists"]

def tournament_lists_analysis(name, groups):
    tournament_lists = get_tournament_lists(name, groups)
    objective_card_dict = {}
    deployment_card_dict = {}
    condition_card_dict = {}
    command_card_dict = {}
    units_dict = {}
    upgrades_card_dict = {}
    for tlist in tournament_lists:
        objective_card_dict, deployment_card_dict, condition_card_dict = \
            get_battlefield_cards(tlist, objective_card_dict, deployment_card_dict, condition_card_dict)
        command_card_dict = get_command_cards(tlist, command_card_dict)
        units_dict, upgrades_card_dict = get_unit_cards(tlist, units_dict, upgrades_card_dict)
    objective_card_dict = dict(sorted(objective_card_dict.items(), key=lambda x:x[1], reverse=True))
    deployment_card_dict = dict(sorted(deployment_card_dict.items(), key=lambda x:x[1], reverse=True))
    condition_card_dict = dict(sorted(condition_card_dict.items(), key=lambda x:x[1], reverse=True))
    command_card_dict = dict(sorted(command_card_dict.items(), key=lambda x:x[1], reverse=True))
    units_dict = dict(sorted(units_dict.items(), key=lambda x:x[1], reverse=True))
    upgrades_card_dict = dict(sorted(upgrades_card_dict.items(), key=lambda x:x[1], reverse=True))
    return {'Objectives': objective_card_dict,
            'Deployments': deployment_card_dict,
            'Conditions': condition_card_dict,
            'Command Cards': command_card_dict,
            'Units': units_dict,
            'Upgrades': upgrades_card_dict}

def battlefield_card_analysis(name):
    tournament_lists = get_tournament_lists(name)
    objective_card_dict = {}
    deployment_card_dict = {}
    condition_card_dict = {}
    for tlist in tournament_lists:
        objective_card_dict, deployment_card_dict, condition_card_dict = \
            get_battlefield_cards(tlist, objective_card_dict, deployment_card_dict, condition_card_dict)
    objective_card_dict = dict(sorted(objective_card_dict.items(), key=lambda x:x[1], reverse=True))
    deployment_card_dict = dict(sorted(deployment_card_dict.items(), key=lambda x:x[1], reverse=True))
    condition_card_dict = dict(sorted(condition_card_dict.items(), key=lambda x:x[1], reverse=True))
    return objective_card_dict, deployment_card_dict, condition_card_dict
    
def get_battlefield_cards(tlist, objective_card_dict, deployment_card_dict, condition_card_dict):
    battlefield_cards = tlist["battlefieldCards"]
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
    return objective_card_dict, deployment_card_dict, condition_card_dict

def command_card_analysis(name):
    tournament_lists = get_tournament_lists(name)
    command_card_dict = {}
    for tlist in tournament_lists:
        command_card_dict = get_command_cards(tlist, command_card_dict)
    command_card_dict = dict(sorted(command_card_dict.items(), key=lambda x:x[1], reverse=True))
    return command_card_dict
    
def get_command_cards(tlist, command_card_dict):
    command_cards = tlist["commandCards"]
    for ccard in command_cards:
        if ccard["card"]["name"] in command_card_dict:
            command_card_dict[ccard["card"]["name"]] += 1
        else:
            command_card_dict[ccard["card"]["name"]] = 1
    return command_card_dict

def unit_card_analysis(name):
    tournament_lists = get_tournament_lists(name)
    units_dict = {}
    upgrades_card_dict = {}
    for tlist in tournament_lists:
        units_dict, upgrades_card_dict = get_unit_cards(tlist, units_dict, upgrades_card_dict)
    units_dict = dict(sorted(units_dict.items(), key=lambda x:x[1], reverse=True))
    upgrades_card_dict = dict(sorted(upgrades_card_dict.items(), key=lambda x:x[1], reverse=True))
    return units_dict, upgrades_card_dict
    
def get_unit_cards(tlist, units_dict, upgrades_card_dict):
    unit_cards = tlist["units"]
    for unit_card in unit_cards:
        if unit_card["card"]["name"] in units_dict:
            units_dict[unit_card["card"]["name"]] += 1
        else:
            units_dict[unit_card["card"]["name"]] = 1
        upgrade_cards = unit_card["upgrades"]
        if len(upgrade_cards) > 0:
            for up_card in upgrade_cards:
                if up_card["card"]["name"] in upgrades_card_dict:
                    upgrades_card_dict[up_card["card"]["name"]] += 1
                else:
                    upgrades_card_dict[up_card["card"]["name"]] = 1
    return units_dict, upgrades_card_dict

def main():
    print("Include Mirrored:",calculate_faction_win_rate("cherokee-open-2024", True, None))
    print("Don't Include Mirrored:",calculate_faction_win_rate("cherokee-open-2024", False, None))
    # pprint.pprint(tournament_lists_analysis("cherokee-open-2024"), sort_dicts=False)
    
if __name__ == '__main__':
    main()