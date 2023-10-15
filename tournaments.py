import db
import service
import tournament

def update_recent_elos(start_date, end_date):
    tournaments = service.get_all_tournaments(start_date, end_date)
    for tournament_name in tournaments:
        tournament.update_tournament_data(tournament_name)
        
def main():
    update_recent_elos("2022-11-01 12:00:00", "2022-11-17 02:00:00")
    print(db.get_all())

if __name__ == '__main__':
    main()