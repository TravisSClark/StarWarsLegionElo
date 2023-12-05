#external
import math

startingElo = 800

# Match score diff
K = 30

# player_one_winner is a boolean
def elo_rating(player_one_elo, player_two_elo, player_one_winner):
    prob_two = probability(player_one_elo, player_two_elo)
    prob_one = 1 - prob_two
 
    player_one_elo = update_elo(player_one_elo, prob_one, player_one_winner)
    player_two_elo = update_elo(player_two_elo, prob_two, not player_one_winner)
    return player_one_elo, player_two_elo

def weighted_elo_rating(weighted_player_one_elo, weighted_player_two_elo, player_one_winner):
    weighted_player_one_elo, weighted_player_two_elo = elo_rating(weighted_player_one_elo, weighted_player_two_elo, player_one_winner)
    return weighted_player_one_elo + K / 3, weighted_player_two_elo + K / 3

def probability(rating1, rating2):
    return 1 * 1/ (1 + 1 * math.pow(10, 1 * (rating1 - rating2) / 400))

def update_elo(rating, expected, d):
    actual = 1 if d else 0
    return round(rating + K * (actual - expected))

def main():
    print(elo_rating(823, 798, True))
    
if __name__ == '__main__':
    main()