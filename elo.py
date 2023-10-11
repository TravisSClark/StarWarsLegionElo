import math

startingElo = 800

# Match score diff
K = 30

def probability(rating1, rating2):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))

def elo_rating(Ra, Rb, d):
    Pb = probability(Ra, Rb)
    Pa = 1 - Pb
 
    Ra = update_elo(Ra, Pa, d)
    Rb = update_elo(Rb, Pb, not d)

def update_elo(rating, expected, d):
    actual = 1 if d else 0
    
    return rating + K * (actual - expected)