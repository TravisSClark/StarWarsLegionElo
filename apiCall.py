import json
import requests

url = 'https://api.gameuplink.com/graphql/'

headers = {"content-type":"application/json",
           "Origin":"https://legion.gameuplink.com"}

def getAllTournaments(startDate, endDate, currentPage):
    f = open("Legion Tournament Elos/getAllRequestBody.json")
    getAllRequestBody = json.load(f)
    getAllRequestBody["variables"]["startsAtRange"]["from"] = startDate
    getAllRequestBody["variables"]["startsAtRange"]["to"] = endDate
    getAllRequestBody["variables"]["page"] = currentPage
    return requests.post(url=url, json=getAllRequestBody, headers=headers)

def getTournamentData(name):
    print("Hello world")