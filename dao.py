import api

def get_all_tournaments(start_date, end_date):
    list_of_tournaments = []
    current_page = 1
    response = api.get_all_tournaments(start_date, end_date, current_page).json()["data"]["tournaments"]
    list_of_tournaments.extend(get_tournament_names(response))
    #lastPage = response["paginatorInfo"]["lastPage"]
    while current_page < 3:
        current_page += 1
        response = api.get_all_tournaments(start_date, end_date, current_page).json()["data"]["tournaments"]
        list_of_tournaments.extend(get_tournament_names(response))
    return list_of_tournaments

def get_tournament_groups(name):
    return api.get_tournament_data(name).json()["data"]["tournament"]["groups"]

def get_tournament_names(response):
    minimum_player_count = 16
    tournaments = []
    page_tournament_list = response["data"]
    for tournament in page_tournament_list:
        if tournament["playerCount"] >= minimum_player_count:
            tournaments.append(tournament["slug"])
    return tournaments

# def main():
#     print(get_all_tournaments("2022-11-01 12:00:00", "2023-10-08 02:00:00"))
#     print(get_tournament_groups("house-of-cards-store-championship"))
        
    
# if __name__ == '__main__':
#     main()