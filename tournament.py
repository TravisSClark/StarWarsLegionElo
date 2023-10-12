import service
import db
import elo

def update_tournament_data(name):
    groups = service.get_tournament_groups(name)
    for group in groups:
        for round in group["rounds"]:
            for match in round["matches"]:
                if not match["isBye"]:
                    player_one = get_player_info_from_db(match["playerOne"]["user"])
                    player_two = get_player_info_from_db(match["playerTwo"]["user"])
                    winner = match["winner"]["user"]
                    player_one_winner = player_one["id"] == int(winner["id"])
                    player_one["elo"], player_two["elo"] = elo.elo_rating(player_one["elo"], player_two["elo"], player_one_winner)
                    db.update_player(player_one["id"], player_one["name"], player_one["elo"])
                    db.update_player(player_two["id"], player_two["name"], player_two["elo"])
                

def get_player_info_from_db(player_info):
    db_player = db.get_player(int(player_info["id"]))
    #db_player = db.get_player(0)
    if db_player == None:
        db.insert_player(player_info["id"], player_info["name"])
        db_player = db.get_player(int(player_info["id"]))    
    return db_player

def main():
    update_tournament_data("house-of-cards-store-championship")
    print(db.get_all().sort(key = lambda i:i[2], reverse = True))
        
    
if __name__ == '__main__':
    main()