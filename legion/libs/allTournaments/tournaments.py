# internal
import tournamentsService
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import dataAccess.eloDb as eloDb
import libs.tournament as tournament
import util.automation as automation

# external
import json

def update_elos(start_date, end_date):
    tournaments = tournamentsService.get_all_tournaments(start_date, end_date)
    for tournament_name in tournaments:
        _, tournament_date = tournament.update_tournament_data(tournament_name)
        automation.decay_elo(tournament_date)
        
def get_all():
    players = eloDb.get_all()
    return players
        
def main():
    update_elos("2022-11-01 12:00:00", "2024-02-26 01:00:00")
    # update_elos("2023-12-04 01:00:00", "2024-02-20 01:00:00")
    players = eloDb.get_all()
    weightedPlayers = eloDb.get_all_sorted("weighted_elo")
    with open("legion/data/response/getAll.json", "w", encoding='utf8') as file:
        file.write("[\n")
        for player in players:
            json.dump(player, file, ensure_ascii=False)
            file.write(",\n")
        file.write("{}\n]")
        players = eloDb.get_all()
    with open("legion/data/response/getAllWeighted.json", "w", encoding='utf8') as file:
        file.write("[\n")
        for wp in weightedPlayers:
            json.dump(wp, file, ensure_ascii=False)
            file.write(",\n")
        file.write("{}\n]")
        
if __name__ == '__main__':
    main()