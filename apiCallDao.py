import apiCall

def getAllTournaments(startDate, endDate):
    listOfTournaments = []
    currentPage = 1
    response = apiCall.getAllTournaments(startDate, endDate, currentPage).json()["data"]["tournaments"]
    listOfTournaments.extend(getTournamentsFromList(response))
    #lastPage = response["paginatorInfo"]["lastPage"]
    while currentPage < 3:
        currentPage += 1
        response = apiCall.getAllTournaments(startDate, endDate, currentPage).json()["data"]["tournaments"]
        listOfTournaments.extend(getTournamentsFromList(response))
    return listOfTournaments

def getTournamentData(name):
    return apiCall.getTournamentData(name).json()["data"]["tournament"]["groups"]

def getTournamentsFromList(response):
    minimumPlayerCount = 16
    tournaments = []
    pageTournamentList = response["data"]
    for tournament in pageTournamentList:
        if tournament["playerCount"] >= minimumPlayerCount:
            tournaments.append(tournament["slug"])
    return tournaments

print(getAllTournaments("2022-11-01 12:00:00", "2023-10-08 02:00:00"))
print(getTournamentData("house-of-cards-store-championship"))