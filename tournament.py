import dao

def get_tournament_data(name):
    groups = dao.getTournamentGroups(name)
    for group in groups:
        print("hello world")

def get_player_info():
    print("hello world")
    
print(get_tournament_data("house-of-cards-store-championship"))