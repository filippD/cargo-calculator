import airportsdata

class Airports:
    def find(params):
        airports = airportsdata.load('IATA')
        query = params["search_query"].lower()
        result = []
        for key in airports:
          airport = airports[key]
          if query in airport["iata"].lower():
            result.append(airport)

        if len(result) < 10:
          for key in airports:
            airport = airports[key]
            if query in airport["name"].lower() and airport not in result:
              result.append(airport)
        return result[:10]
