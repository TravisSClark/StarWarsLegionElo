import math

startingElo = 800

# Match score diff
K = 30

def Probability(rating1, rating2):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))

def EloRating(Ra, Rb, d):
    Pb = Probability(Ra, Rb)
    Pa = 1 - Pb
 
    Ra = UpdateElo(Ra, Pa, d)
    Rb = UpdateElo(Rb, Pb, not d)

def UpdateElo(rating, expected, d):
    actual = 1 if d else 0
    
    return rating + K * (actual - expected)