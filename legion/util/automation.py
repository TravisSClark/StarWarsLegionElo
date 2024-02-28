from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dataAccess.eloDb as eloDb
import elo

def decay_player_elo(player_list, date):
    for player in player_list:
        player["weighted_elo"] -= elo.K
        player["bonus_points"] += elo.K
        player["change"] = -abs(elo.K)
        player["change_date"] = date
    return player_list

def six_months_ago(date):
    date_minus_six = date - relativedelta(months=1)
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    new_date_format = '%Y%m%d'
    date_minus_six = int(datetime.strptime(str(date_minus_six), date_format).strftime(new_date_format))
    return date_minus_six

def decay_elo(date):
    shifted_date = six_months_ago(date)
    players_list = eloDb.get_players_not_played_since_date(shifted_date)
    players_list = decay_player_elo(players_list, shifted_date)
    eloDb.bulk_update_players(players_list)
    return players_list

def main():
    print(decay_elo(datetime.now()))

if __name__ == '__main__':
    main()