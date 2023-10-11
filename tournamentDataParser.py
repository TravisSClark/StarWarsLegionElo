import apiCallDao

def get_tournament_data(name):
    groups = apiCallDao.getTournamentGroups(name)
    for group in groups:
        print("hello world")

def getPlayerInfo():
    print("hello world")
    
print(get_tournament_data("house-of-cards-store-championship"))