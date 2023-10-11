import requests

url = 'https://api.gameuplink.com/graphql/'

headers = {"content-type":"application/json",
           "Origin":"https://legion.gameuplink.com"}

getAllRequestBody = {
    "query": "\n    query GetAllTournaments($name: String, $first: Int, $page: Int, $startsAt: DateTime, $startsAtRange: DateRange, $endsAt: DateTime, $orderBy: [QueryTournamentsOrderByOrderByClause!], $includeCancelled: Boolean = false) {\n  tournaments(\n    name: $name\n    first: $first\n    page: $page\n    startsAt: $startsAt\n    startsAtRange: $startsAtRange\n    endsAt: $endsAt\n    orderBy: $orderBy\n    includeCancelled: $includeCancelled\n  ) {\n    data {\n      id\n      slug\n      name\n      playerCount\n      startsAt\n      endsAt\n      cancelledAt\n      venue\n      country\n      region\n    }\n    paginatorInfo {\n      count\n      currentPage\n      firstItem\n      hasMorePages\n      lastItem\n      lastPage\n      perPage\n      total\n    }\n  }\n}\n    ",
    "variables": {
        "name": "%%",
        "page": 1,
        "orderBy": [
            {
                "column": "STARTS_AT",
                "order": "ASC"
            }
        ],
        "includeCancelled": False,
        "startsAtRange": {
            "from": "",
            "to": ""
        }
    },
    "operationName": "GetAllTournaments"
}

def getAllTournaments(startDate, endDate, currentPage):
    getAllRequestBody["variables"]["startsAtRange"]["from"] = startDate
    getAllRequestBody["variables"]["startsAtRange"]["to"] = endDate
    getAllRequestBody["variables"]["page"] = currentPage
    return requests.post(url=url, json=getAllRequestBody, headers=headers)

def getTournamentData(name):
    print("Hello world")