# external
import json
import requests

url = 'https://api.gameuplink.com/graphql/'

headers = {"content-type":"application/json",
           "Origin":"https://legion.gameuplink.com"}

def get_all_tournaments(start_date, end_date, current_page):
    f = open("legion/data/request/getAllRequestBody.json")
    get_all_request_body = json.load(f)
    get_all_request_body["variables"]["startsAtRange"]["from"] = start_date
    get_all_request_body["variables"]["startsAtRange"]["to"] = end_date
    get_all_request_body["variables"]["page"] = current_page
    return requests.post(url=url, json=get_all_request_body, headers=headers)

def get_tournament_data(name):
    f = open("legion/data/request/getTournamentRequestBody.json")
    get_tournament_request_body = json.load(f)
    get_tournament_request_body["variables"]["slug"] = name
    attempts = 0
    while attempts < 3:
        response = requests.post(url=url, json=get_tournament_request_body, headers=headers)
        if response.status_code == 200:
            return response.json()["data"]["tournament"]
        else:
            attempts += 1
            
def get_tournament_lists(player_id_list):
    f = open("legion/data/request/getListsRequestBody.json")
    get_lists_request_body = json.load(f)
    get_lists_request_body["variables"]["playerIds"] = player_id_list
    return requests.post(url=url, json=get_lists_request_body, headers=headers)