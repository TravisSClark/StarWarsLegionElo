import service
import db
import elo

def update_tournament_data(name):
    groups = service.get_tournament_groups(name)
    for group in groups:
        player_list, player_id_elo_dict = get_player_info_from_db(group["players"])
        for round in group["rounds"]:
            for match in round["matches"]:
                if not match["isBye"]:
                    player_one_id = int(match["playerOne"]["user"]["id"])
                    player_two_id = int(match["playerTwo"]["user"]["id"])
                    winner_id = int(match["winner"]["user"]["id"])
                    player_one_winner = player_one_id == winner_id
                    player_id_elo_dict[player_one_id], player_id_elo_dict[player_two_id] = elo.elo_rating(
                        player_id_elo_dict[player_one_id], player_id_elo_dict[player_two_id], player_one_winner)
        for player in player_list:
            player["elo"] = player_id_elo_dict[player["id"]]
            db.update_player(player["id"], player["name"], player["elo"])
                

def get_player_info_from_db(players):
    player_list = []
    player_id_elo_dict = {}
    for player in players:
        db_player = db.get_player(int(player["user"]["id"])) or {}
        if not db_player:
            db.insert_player(player["user"]["id"], player["user"]["name"])
            db_player["id"] = player["user"]["id"]
            db_player["elo"] = db.defaultElo
        db_player["name"] = player["user"]["name"]
        player_list.append(db_player)
        player_id_elo_dict[db_player["id"]] = db_player["elo"]
    return player_list, player_id_elo_dict
        

def main():
    update_tournament_data("house-of-cards-store-championship")
    print(sorted(db.get_all(), key=lambda i: i[2], reverse=True))
    
if __name__ == '__main__':
    main()