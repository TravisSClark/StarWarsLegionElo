#external
import math

# Match score diff
K = 30

# Games before ELO is calculated
max_phantom_games = 8

# player_one_winner is a boolean, weighted is a boolean
def elo_rating(player_one_elo, player_two_elo, player_one_winner):
    prob_one, prob_two = probability(player_one_elo, player_two_elo)
    player_one_elo +=  point_change(prob_one, player_one_winner)
    player_two_elo += point_change(prob_two, not player_one_winner)
    return player_one_elo, player_two_elo

# Could add K / 3 for weight of more games 
def weighted_elo_rating(weighted_player_one_elo, weighted_player_two_elo, player_one_winner,
                        player_one_games, player_one_bonus_points,
                        player_two_games, player_two_bonus_points):
    prob_one, prob_two = probability(weighted_player_one_elo, weighted_player_two_elo)
    player_one_change =  point_change(prob_one, player_one_winner)
    player_two_change = point_change(prob_two, not player_one_winner)
    if player_one_games < max_phantom_games or (player_one_bonus_points > 0 and player_one_winner):
        player_one_change, player_one_bonus_points = weighted_calc(player_one_change, player_one_games, player_one_bonus_points)
    if player_two_games < max_phantom_games or (player_two_bonus_points > 0 and not player_one_winner):
        player_two_change, player_two_bonus_points = weighted_calc(player_two_change, player_two_games, player_two_bonus_points)
    weighted_player_one_elo += player_one_change
    weighted_player_two_elo += player_two_change
    return weighted_player_one_elo, weighted_player_two_elo, player_one_bonus_points, player_two_bonus_points

# something is wrong
def weighted_calc(change, games, bonus_points):
    if games < max_phantom_games:
        change *= 2
    elif bonus_points > 0:
        if bonus_points > change:
            bonus_points -= change
            change *= 2
        else:
            change += bonus_points
            bonus_points = 0
    return change, bonus_points

def probability(rating1, rating2):
    prob_two = 1 * 1/ (1 + 1 * math.pow(10, 1 * (rating1 - rating2) / 400))
    prob_one = 1 - prob_two
    return prob_one, prob_two

# d is a boolen for win or lose
def point_change(expected, d):
    actual = 1 if d else 0
    return round(K * (actual - expected))

def main():
    print(elo_rating(823, 798, True))
    
if __name__ == '__main__':
    main()