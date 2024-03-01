from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dataAccess.eloDb as eloDb
import util.elo as elo

def decay_player_elo(player_list, date):
    for player in player_list:
        player["weighted_elo"] -= elo.K
        player["bonus_points"] += elo.K
        player["change"] = -abs(elo.K)
        player["change_date"] = date
    return player_list

def six_months_ago(date):
    date_minus_six = date - relativedelta(months=6)
    new_date_format = '%Y%m%d'
    date_minus_six = int(date_minus_six.strftime(new_date_format))
    return date_minus_six

def decay_elo(date):
    date_format = '%Y-%m-%d %H:%M:%S'
    date = datetime.strptime(str(date), date_format)
    shifted_date = six_months_ago(date)
    new_date_format = '%Y%m%d'
    date = int(date.strftime(new_date_format))
    players_list = eloDb.get_players_not_played_since_date(shifted_date)
    players_list = [player for player in players_list if player["games"] > elo.max_phantom_games]
    players_list = decay_player_elo(players_list, date)
    eloDb.bulk_update_players(players_list)
    return players_list

def main():
    print(decay_elo(str(datetime.now())))

if __name__ == '__main__':
    main()