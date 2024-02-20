# internal
import db
import service
import tournament

# external
import json

def update_recent_elos(start_date, end_date):
    tournaments = service.get_all_tournaments(start_date, end_date)
    for tournament_name in tournaments:
        tournament.update_tournament_data(tournament_name)
        
def main():
    # update_recent_elos("2022-11-01 12:00:00", "2023-12-04 01:00:00")
    update_recent_elos("2023-12-04 01:00:00", "2024-02-20 01:00:00")
    players = db.get_all()
    weightedPlayers = db.get_all_sorted("weighted_elo")
    with open("getAll.json", "w", encoding='utf8') as file:
        file.write("[\n")
        for player in players:
            json.dump(player, file, ensure_ascii=False)
            file.write(",\n")
        file.write("{}\n]")
        players = db.get_all()
    with open("getAllWeighted.json", "w", encoding='utf8') as file:
        file.write("[\n")
        for wp in weightedPlayers:
            json.dump(wp, file, ensure_ascii=False)
            file.write(",\n")
        file.write("{}\n]")
        

if __name__ == '__main__':
    main()