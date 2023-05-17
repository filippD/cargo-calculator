import airportsdata

class Airports:
    def find(params):
        airports = airportsdata.load('IATA')
        query = params["search_query"].lower()
        result = []
        for key in airports:
          airport = airports[key]
          if query in airport["iata"].lower()  or query in airport["icao"].lower() or query in airport["name"].lower():
            result.append(airport)
        return result[:10]
