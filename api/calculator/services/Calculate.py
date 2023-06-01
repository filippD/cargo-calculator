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
    time_critical = input_dict.get("time_critical")
    general_request = not time_critical
    one_leg = input_dict.get("one_leg")
    charter_focused = input_dict.get("charter_focused")

    # time-critical
    time_critical_priority_for_one_leg_flight = time_critical and one_leg
    time_critical_priority_for_charter_focused_operators = time_critical and charter_focused

    # general
    general_priority_for_one_leg_flight = general_request and one_leg
    general_priority_for_charter_focused_operators = general_request and charter_focused


    # # Define Functions

    # In[152]:


    # distance
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


    # # Import Databases

    # In[153]:


    df_base = pd.read_excel('base.xlsx')
    df_airports = pd.read_csv('airport-codes_csv.csv')
    df_airports[['longitude_deg', 'latitude_deg']] = df_airports.coordinates.str.split(",", expand = True).astype(float)


    # # Transform data to pd.DataFrame

    # In[154]:


    df_base['arr_origin'] = input_dict['arr_origin']
    df_base['arr_destination'] = input_dict['arr_destination']
    df_base['date'] = input_dict['date']
    df_base['payload_kg'] = input_dict['payload']
    df_base['num_flights'] = (df_base['payload_kg'] / df_base['MZFW_Payload']).apply(np.ceil).astype(int)


    # # Load Coordinates

    # In[155]:



    #--------------

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


    # # Load Distances

    # In[156]:


    df_base['flight_distance'] = df_base.apply(lambda row: distance(row.dep_airport_lat, row.dep_airport_long, row.arr_airport_lat, row.arr_airport_long) , axis = 1)
    df_base['empty_distance'] = df_base['flight_distance']

    df_base['ferry_1_virtual_distance'] = df_base.apply(lambda row: distance(row.virtual_base_lat, row.virtual_base_long, row.dep_airport_lat, row.dep_airport_long) , axis = 1)
    df_base['ferry_1_current_distance'] = df_base.apply(lambda row: distance(row.current_location_lat, row.current_location_long, row.dep_airport_lat, row.dep_airport_long) , axis = 1)

    df_base['ferry_2_distance'] = df_base.apply(lambda row: distance(row.arr_airport_lat, row.arr_airport_long, row.virtual_base_lat, row.virtual_base_long) , axis = 1)


    # # Flight

    # In[157]:


    # Number of Flight legs
    df_base['flight_leg_num'] = np.ceil(df_base['payload_kg'] / df_base['MZFW_Payload'])

    # Payload per Flight leg
    df_base['flight_leg_payload'] = df_base['payload_kg'] / df_base['flight_leg_num']

    # Payload Range Interval per Flight leg
    # Condition A --------
    df_base.loc[df_base['flight_leg_payload'] == df_base['MZFW_Payload'], 'flight_leg_payload_range_interval'] = 'A'
    # Condition B --------
    df_base.loc[(df_base['flight_leg_payload'] < df_base['MZFW_Payload']) & (df_base['flight_leg_payload'] >= df_base['MFW_Payload']), 'flight_leg_payload_range_interval'] = 'B'
    # Condition C --------
    df_base.loc[(df_base['flight_leg_payload'] < df_base['MFW_Payload']) & (df_base['flight_leg_payload'] >= df_base['OEW_Payload']), 'flight_leg_payload_range_interval'] = 'C'

    # Number of Flight leg segments
    # Condition A --------
    df_base.loc[df_base['flight_leg_payload_range_interval'] == 'A', 'flight_leg_segm_num'] = np.ceil(df_base['flight_distance'] / df_base['MZFW_Range'])
    # Condition B --------
    df_base.loc[df_base['flight_leg_payload_range_interval'] == 'B', 'flight_leg_segm_num'] = np.ceil(df_base['flight_distance'] / (df_base['MZFW_Range'] + (df_base['MZFW_Payload'] - df_base['flight_leg_payload']) * (df_base['MFW_Range'] - df_base['MZFW_Range']) / (df_base['MZFW_Payload'] - df_base['MFW_Payload'])))
    # Condition C --------
    df_base.loc[df_base['flight_leg_payload_range_interval'] == 'C', 'flight_leg_segm_num'] = np.ceil(df_base['flight_distance'] / (df_base['MFW_Range'] + (df_base['MFW_Payload'] - df_base['flight_leg_payload']) * (df_base['OEW_Range'] - df_base['MFW_Range']) / (df_base['MFW_Payload'])))

    # Distance of each Flight segment
    df_base['flight_leg_segm_distance'] = df_base['flight_distance'] / df_base['flight_leg_segm_num']

    # Speed of each Flight segment
    df_base['flight_leg_segm_speed'] = df_base.apply(lambda row: v(row.flight_leg_segm_distance, row.v_max, row.k_m) , axis = 1)

    # Time of each Flight segment
    df_base['flight_leg_segm_time'] = df_base['flight_leg_segm_distance'] / df_base['flight_leg_segm_speed']

    # Fuel of each Flight segment
    # Condition A --------
    df_base.loc[df_base['flight_leg_payload_range_interval'] == 'A', 'flight_leg_segm_fuel_kg'] = df_base['MZFW_Fuel'] * (df_base['flight_leg_segm_distance'] / df_base['MZFW_Range'])
    # Condition B --------
    df_base.loc[df_base['flight_leg_payload_range_interval'] == 'B', 'flight_leg_segm_fuel_kg'] = df_base['MFM_Fuel'] * (df_base['flight_leg_segm_distance'] / df_base['MFW_Range'])
    # Condition C --------
    df_base.loc[df_base['flight_leg_payload_range_interval'] == 'C', 'flight_leg_segm_fuel_kg'] = df_base['OEW_Fuel'] * (df_base['flight_leg_segm_distance'] / df_base['OEW_Range'])

    # Total Flight Time
    df_base['flight_time'] = df_base['flight_leg_num'] * df_base['flight_leg_segm_num'] * df_base['flight_leg_segm_time']

    # Total Flight Cost
    df_base['flight_cost'] = df_base['flight_leg_num'] * df_base['flight_leg_segm_num'] * ((df_base['flight_leg_segm_time'] * df_base['acmi_h']) + (df_base['flight_leg_segm_fuel_kg'] * (df_base['fuel_price_kg'] + df_base['co2_price_kg'])))


    # # Empty Leg

    # In[158]:


    # Number of Empty legs
    df_base['empty_leg_num'] = df_base['flight_leg_num'] - 1

    # Payload per Empty leg
    df_base['empty_leg_payload'] = 0

    # Payload Range Interval per Empty leg
    # Condition A --------
    df_base.loc[df_base['empty_leg_payload'] == df_base['MZFW_Payload'], 'empty_leg_payload_range_interval'] = 'A'
    # Condition B --------
    df_base.loc[(df_base['empty_leg_payload'] < df_base['MZFW_Payload']) & (df_base['empty_leg_payload'] >= df_base['MFW_Payload']), 'empty_leg_payload_range_interval'] = 'B'
    # Condition C --------
    df_base.loc[(df_base['empty_leg_payload'] < df_base['MFW_Payload']) & (df_base['empty_leg_payload'] >= df_base['OEW_Payload']), 'empty_leg_payload_range_interval'] = 'C'

    # Number of Flight leg segments
    # Condition A --------
    df_base.loc[df_base['empty_leg_payload_range_interval'] == 'A', 'empty_leg_segm_num'] = np.ceil(df_base['flight_distance'] / df_base['MZFW_Range'])
    # Condition B --------
    df_base.loc[df_base['empty_leg_payload_range_interval'] == 'B', 'empty_leg_segm_num'] = np.ceil(df_base['flight_distance'] / (df_base['MZFW_Range'] + (df_base['MZFW_Payload'] - df_base['empty_leg_payload']) * (df_base['MFW_Range'] - df_base['MZFW_Range']) / (df_base['MZFW_Payload'] - df_base['MFW_Payload'])))
    # Condition C --------
    df_base.loc[df_base['empty_leg_payload_range_interval'] == 'C', 'empty_leg_segm_num'] = np.ceil(df_base['flight_distance'] / (df_base['MFW_Range'] + (df_base['MFW_Payload'] - df_base['empty_leg_payload']) * (df_base['OEW_Range'] - df_base['MFW_Range']) / (df_base['MFW_Payload'])))

    # Distance of each Flight segment
    df_base['empty_leg_segm_distance'] = df_base['empty_distance'] / df_base['empty_leg_segm_num']

    # Speed of each Flight segment
    df_base['empty_leg_segm_speed'] = df_base.apply(lambda row: v(row.flight_leg_segm_distance, row.v_max, row.k_m) , axis = 1)

    # Time of each Flight segment
    df_base['empty_leg_segm_time'] = df_base['empty_leg_segm_distance'] / df_base['empty_leg_segm_speed']

    # Fuel of each Flight segment
    # Condition A --------
    df_base.loc[df_base['empty_leg_payload_range_interval'] == 'A', 'empty_leg_segm_fuel_kg'] = df_base['MZFW_Fuel'] * (df_base['empty_leg_segm_distance'] / df_base['MZFW_Range'])
    # Condition B --------
    df_base.loc[df_base['empty_leg_payload_range_interval'] == 'B', 'empty_leg_segm_fuel_kg'] = df_base['MFM_Fuel'] * (df_base['empty_leg_segm_distance'] / df_base['MFW_Range'])
    # Condition C --------
    df_base.loc[df_base['empty_leg_payload_range_interval'] == 'C', 'empty_leg_segm_fuel_kg'] = df_base['OEW_Fuel'] * (df_base['empty_leg_segm_distance'] / df_base['OEW_Range'])

    # Total Flight Time
    df_base['empty_time'] = df_base['empty_leg_num'] * df_base['empty_leg_segm_num'] * df_base['empty_leg_segm_time']

    # Total Flight Cost
    df_base['empty_cost'] = df_base['empty_leg_num'] * df_base['empty_leg_segm_num'] * ((df_base['empty_leg_segm_time'] * df_base['acmi_h']) + (df_base['empty_leg_segm_fuel_kg'] * (df_base['fuel_price_kg'] + df_base['co2_price_kg'])))


    # # Ferry 1 Virtual

    # In[159]:


    # Number of Ferry 1 segments
    df_base['ferry_1_virtual_segm_num'] = np.ceil(df_base['ferry_1_virtual_distance'] / df_base['OEW_Range'])

    # Distance of each Ferry 1 segment
    df_base['ferry_1_virtual_segm_distance'] = np.where(df_base['ferry_1_virtual_segm_num'] == 0, 0, df_base['ferry_1_virtual_distance'] / df_base['ferry_1_virtual_segm_num'])

    # Speed of each Ferry 1 segment
    df_base['ferry_1_virtual_segm_speed'] = df_base.apply(lambda row: v(row.ferry_1_virtual_segm_distance, row.v_max, row.k_m) , axis = 1)

    # Time of each Ferry 1 segment
    df_base['ferry_1_virtual_segm_time'] = np.where(df_base['ferry_1_virtual_segm_speed'] > 0, df_base['ferry_1_virtual_segm_distance'] / df_base['ferry_1_virtual_segm_speed'], 0)

    # Fuel of each Ferry 1 segment
    df_base['ferry_1_virtual_segm_fuel_kg'] = df_base['OEW_Fuel'] * (df_base['ferry_1_virtual_segm_distance'] / df_base['OEW_Range'])

    # Total Ferry 1 Time
    df_base['ferry_1_virtual_time'] = df_base['ferry_1_virtual_segm_num'] * df_base['ferry_1_virtual_segm_time']

    # Total Ferry 1 Cost
    df_base['ferry_1_virtual_cost'] = df_base['ferry_1_virtual_segm_num'] * ((df_base['ferry_1_virtual_segm_time'] * df_base['acmi_h']) + (df_base['ferry_1_virtual_segm_fuel_kg'] * (df_base['fuel_price_kg'] + df_base['co2_price_kg'])))


    # # Ferry 1 Current

    # In[160]:


    # Number of Ferry 1 segments
    df_base['ferry_1_current_segm_num'] = np.ceil(df_base['ferry_1_current_distance'] / df_base['OEW_Range'])

    # Distance of each Ferry 1 segment
    df_base['ferry_1_current_segm_distance'] = np.where(df_base['ferry_1_current_segm_num'] == 0, 0, df_base['ferry_1_current_distance'] / df_base['ferry_1_current_segm_num'])

    # Speed of each Ferry 1 segment
    df_base['ferry_1_current_segm_speed'] = df_base.apply(lambda row: v(row.ferry_1_current_segm_distance, row.v_max, row.k_m) , axis = 1)

    # Time of each Ferry 1 segment
    df_base['ferry_1_current_segm_time'] = np.where(df_base['ferry_1_current_segm_speed'] > 0, df_base['ferry_1_current_segm_distance'] / df_base['ferry_1_current_segm_speed'], 0)

    # Fuel of each Ferry 1 segment
    df_base['ferry_1_current_segm_fuel_kg'] = df_base['OEW_Fuel'] * (df_base['ferry_1_current_segm_distance'] / df_base['OEW_Range'])

    # Total Ferry 1 Time
    df_base['ferry_1_current_time'] = df_base['ferry_1_current_segm_num'] * df_base['ferry_1_current_segm_time']

    # Total Ferry 1 Cost
    df_base['ferry_1_current_cost'] = df_base['ferry_1_current_segm_num'] * ((df_base['ferry_1_current_segm_time'] * df_base['acmi_h']) + (df_base['ferry_1_current_segm_fuel_kg'] * (df_base['fuel_price_kg'] + df_base['co2_price_kg'])))


    # # Ferry 2

    # In[161]:


    # Number of Ferry 2 segments
    df_base['ferry_2_segm_num'] = np.ceil(df_base['ferry_2_distance'] / df_base['OEW_Range'])

    # Distance of each Ferry 2 segment
    df_base['ferry_2_segm_distance'] = df_base['ferry_2_distance'] / df_base['ferry_2_segm_num']

    # Speed of each Ferry 2 segment
    df_base['ferry_2_segm_speed'] = df_base.apply(lambda row: v(row.ferry_2_segm_distance, row.v_max, row.k_m) , axis = 1)

    # Time of each Ferry 2 segment
    df_base['ferry_2_segm_time'] = df_base['ferry_2_segm_distance'] / df_base['ferry_2_segm_speed']

    # Fuel of each Ferry 2 segment
    df_base['ferry_2_segm_fuel_kg'] = df_base['OEW_Fuel'] * (df_base['ferry_2_segm_distance'] / df_base['OEW_Range'])

    # Total Ferry 2 Time
    df_base['ferry_2_time'] = df_base['ferry_2_segm_num'] * df_base['ferry_2_segm_time']

    # Total Ferry 2 Cost
    df_base['ferry_2_cost'] = df_base['ferry_2_segm_num'] * ((df_base['ferry_2_segm_time'] * df_base['acmi_h']) + (df_base['ferry_2_segm_fuel_kg'] * (df_base['fuel_price_kg'] + df_base['co2_price_kg'])))                                                   


    # # Time-critical quotations

    # In[162]:


    # Time
    df_base['flight_time'] = df_base['flight_time']
    df_base['empty_time'] = df_base['empty_time']
    df_base['ferry_time'] = np.minimum(df_base['ferry_1_virtual_time'], df_base['ferry_1_current_time'])  + df_base['ferry_2_time']

    # Cost
    df_base['flight_cost'] = df_base['flight_cost']
    df_base['empty_cost'] = df_base['empty_cost']
    df_base['ferry_cost'] = np.minimum(df_base['ferry_1_virtual_cost'], df_base['ferry_1_current_cost']) + df_base['ferry_2_cost']

    # Price
    df_base['price'] = (df_base['flight_cost'] + df_base['empty_cost'] + df_base['ferry_cost']) * (1+df_base['margin_h'])

    # df_filter
    if time_critical_priority_for_one_leg_flight == True and time_critical_priority_for_charter_focused_operators == True:
        df_base = df_base.sort_values(by=['charter_focus', 'num_flights', 'price'], ascending=[False, True, True]).reset_index(drop=True)
        
    if time_critical_priority_for_one_leg_flight == True and time_critical_priority_for_charter_focused_operators != True:
        df_base = df_base.sort_values(by=['num_flights', 'price'], ascending=[True, True]).reset_index(drop=True)
        
    if time_critical_priority_for_one_leg_flight != True and time_critical_priority_for_charter_focused_operators == True:
        df_base = df_base.sort_values(by=['charter_focus', 'price'], ascending=[False, True]).reset_index(drop=True)
        
    if time_critical_priority_for_one_leg_flight != True and time_critical_priority_for_charter_focused_operators != True:
        df_base = df_base.sort_values(by=['price'], ascending=[True]).reset_index(drop=True)

    # df_output
    df_output = pd.DataFrame()
    df_output['DEP'] = df_base['arr_origin']
    df_output['ARR'] = df_base['arr_destination']
    df_output['Reg'] = df_base['reg']
    df_output['Operator'] = df_base['operator']
    df_output['Aircraft'] = df_base['type_text']
    df_output['Flight Time'] = df_base['flight_time']
    df_output['Flight Time'] = df_output['Flight Time'].apply(lambda x: '{1}h {0}min'.format(round((x % 1)*60), round((x - (x % 1)))))
    df_output['Number of Flights'] = df_base['num_flights'].apply(lambda x: '{} leg'.format(x))
    df_output['Payload m3'] = df_base['Volume']
    df_output['Payload kg'] = df_base['MZFW_Payload']
    df_output['Price'] = df_base['price']
    df_output['Price'] = df_output['Price'].apply(lambda x: "{:,.0f} USD".format((x)))
    df_output['Contact'] = df_base['contact']

    # dict_output
    dict_output_time_critical = df_output.to_dict('records')


    dict_output_time_critical


    # # General quotations

    # In[163]:


    # Time
    df_base['flight_time'] = df_base['flight_time']
    df_base['empty_time'] = df_base['empty_time']
    df_base['ferry_time'] = df_base['ferry_1_virtual_time'] + df_base['ferry_2_time']

    # Cost
    df_base['flight_cost'] = df_base['flight_cost']
    df_base['empty_cost'] = df_base['empty_cost']
    df_base['ferry_cost'] = df_base['ferry_1_virtual_cost'] + df_base['ferry_2_cost']

    # Price
    df_base['price'] = (df_base['flight_cost'] + df_base['empty_cost'] + df_base['ferry_cost']) * (1+df_base['margin_h'])

    # df_filter
    if general_priority_for_one_leg_flight == True and general_priority_for_charter_focused_operators == True:
        df_base = df_base.sort_values(by=['charter_focus', 'num_flights', 'price'], ascending=[False, True, True]).reset_index(drop=True)
        
    if general_priority_for_one_leg_flight == True and general_priority_for_charter_focused_operators != True:
        df_base = df_base.sort_values(by=['num_flights', 'price'], ascending=[True, True]).reset_index(drop=True)
        
    if general_priority_for_one_leg_flight != True and general_priority_for_charter_focused_operators == True:
        df_base = df_base.sort_values(by=['charter_focus', 'price'], ascending=[False, True]).reset_index(drop=True)
        
    if general_priority_for_one_leg_flight != True and general_priority_for_charter_focused_operators != True:
        df_base = df_base.sort_values(by=['price'], ascending=[True]).reset_index(drop=True)

        
    # df_output
    df_output = pd.DataFrame()
    df_output['DEP'] = df_base['arr_origin']
    df_output['ARR'] = df_base['arr_destination']
    df_output['Reg'] = df_base['reg']
    df_output['Operator'] = df_base['operator']
    df_output['Aircraft'] = df_base['type_text']
    df_output['Flight Time'] = df_base['flight_time']
    df_output['Flight Time'] = df_output['Flight Time'].apply(lambda x: '{1}h {0}min'.format(round((x % 1)*60), round((x - (x % 1)))))
    df_output['Number of Flights'] = df_base['num_flights'].apply(lambda x: '{} leg'.format(x))
    df_output['Payload m3'] = df_base['Volume']
    df_output['Payload kg'] = df_base['MZFW_Payload']
    df_output['Price'] = df_base['price']
    df_output['Price'] = df_output['Price'].apply(lambda x: "{:,.0f} USD".format((x)))
    df_output['Contact'] = df_base['contact']

    # dict_output
    dict_output_general = df_output.to_dict('records')


    return dict_output_general

