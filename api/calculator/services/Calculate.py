import pandas as pd

import numpy as np
import numpy.linalg as lin
import math

import datetime as dt

class Calculate:
  def __init__(self, params):
    self.params = params

  def call(self):
    input_dict = self.params

    def distance(lat1, lon1, lat2, lon2):
      R = 6371  # radius of the earth in km
      dLat = math.radians(lat2 - lat1)
      dLon = math.radians(lon2 - lon1)
      lat1 = math.radians(lat1)
      lat2 = math.radians(lat2)

      a = math.sin(dLat / 2) * math.sin(dLat / 2) +         math.sin(dLon / 2) * math.sin(dLon / 2) * math.cos(lat1) * math.cos(lat2)
      c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
      d = R * c  # distance in km
      return d

# speed
    def v(s, v_max, k_m):
        return (v_max * s) / (k_m + s)

    df_base = pd.read_excel('base.xlsx')
    df_airports = pd.read_csv('airport-codes_csv.csv')
    df_airports[['longitude_deg', 'latitude_deg']] = df_airports.coordinates.str.split(",", expand = True).astype(float)
    df_base['arr_origin'] = input_dict['arr_origin']
    df_base['arr_destination'] = input_dict['arr_destination']
    df_base['date'] = input_dict['date']
    df_base['payload_kg'] = input_dict['payload']
    df_base['num_flights'] = (df_base['payload_kg'] / df_base['ac_payload_kg']).apply(np.ceil).astype(int)

    df_airports_v1 = pd.DataFrame()

    df_airports_v1['arr_origin'] = df_airports['iata_code']
    df_airports_v1['dep_airport_lat'] = df_airports['latitude_deg']
    df_airports_v1['dep_airport_long'] = df_airports['longitude_deg']

    df_base = df_base.merge(df_airports_v1, on='arr_origin', how='left')

    #--------------

    df_airports_v2 = pd.DataFrame()

    df_airports_v2['arr_destination'] = df_airports['iata_code']
    df_airports_v2['arr_airport_lat'] = df_airports['latitude_deg']
    df_airports_v2['arr_airport_long'] = df_airports['longitude_deg']

    df_base = df_base.merge(df_airports_v2, how='left', on='arr_destination')
    
    df_base['flight_distance'] = df_base.apply(lambda row: distance(row.dep_airport_lat, row.dep_airport_long, row.arr_airport_lat, row.arr_airport_long) , axis = 1)
    df_base['ferry_distance_1'] = df_base.apply(lambda row: distance(row.virtual_base_lat, row.virtual_base_long, row.dep_airport_lat, row.dep_airport_long) , axis = 1)
    df_base['ferry_distance_2'] = df_base.apply(lambda row: distance(row.arr_airport_lat, row.arr_airport_long, row.virtual_base_lat, row.virtual_base_long) , axis = 1)

    df_base['flight_speed'] = df_base.apply(lambda row: v(row.flight_distance, row.v_max, row.k_m) , axis = 1)
    df_base['ferry_speed_1'] = df_base.apply(lambda row: v(row.ferry_distance_1, row.v_max, row.k_m) , axis = 1)
    df_base['ferry_speed_2'] = df_base.apply(lambda row: v(row.ferry_distance_2, row.v_max, row.k_m) , axis = 1)

    df_base['flight_time'] = df_base['flight_distance'] / df_base['flight_speed'] * df_base['num_flights']
    df_base['ferry_time'] = df_base['ferry_distance_1'] / df_base['ferry_speed_1'] + df_base['ferry_distance_2'] / df_base['ferry_speed_2'] + df_base['flight_distance'] / df_base['flight_speed'] * (df_base['num_flights'] - 1)

    df_base['price'] = (df_base['flight_time'] + df_base['ferry_time']) * (df_base['acmi_h'] + df_base['doc_h']) * (1+df_base['margin_h'])
    df_base = df_base.sort_values(by=['price']).reset_index(drop=True)

    df_output = pd.DataFrame()

    df_output['DEP'] = df_base['arr_origin']
    df_output['ARR'] = df_base['arr_destination']

    df_output['Reg'] = df_base['reg']
    df_output['Operator'] = df_base['operator']
    df_output['Aircraft'] = df_base['type_text']

    df_output['Flight Time'] = df_base['flight_time']
    df_output['Flight Time'] = df_output['Flight Time'].apply(lambda x: '{1}h {0}min'.format(round((x % 1)*60), round((x - (x % 1)))))
    df_output['Number of Flights'] = df_base['num_flights'].apply(lambda x: '{} leg'.format(x))

    df_output['Payload m3'] = df_base['ac_payload_m3']
    df_output['Payload kg'] = df_base['ac_payload_kg']

    df_output['Price'] = df_base['price']
    df_output['Price'] = df_output['Price'].apply(lambda x: "{:,.0f} USD".format((x)))

    df_output['Contact'] = df_base['contact']

    output_dict = df_output.to_dict('records')

    return(output_dict)
