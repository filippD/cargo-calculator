import airportsdata

import pandas as pd

import numpy as np
import numpy.linalg as lin
import math

import datetime as dt


class Calculate:
  def __init__(self, params):
    self.params = params

  def call(self):
    pd.set_option('display.max_columns', None)
    input_dict = self.params
    time_critical = input_dict.get("time_critical")
    general_request = not time_critical
    one_leg = input_dict.get("one_leg")
    charter_focused = input_dict.get("charter")

    # time-critical
    time_critical_priority_for_one_leg_flight = time_critical and one_leg
    time_critical_priority_for_charter_focused_operators = time_critical and charter_focused

    # general
    general_priority_for_one_leg_flight = general_request and one_leg
    general_priority_for_charter_focused_operators = general_request and charter_focused

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

    # margin
    def m(x, a_margin, b_margin, c_margin, d_margin):
        result = (a_margin * (x - b_margin) ** c_margin + d_margin) / 100
        if isinstance(result, complex):
            return 0.0
        return float(result)


    # Function to select the first 50% smallest rows by 'price' within each group
    def select_smallest(group):
        num_rows = len(group)
        num_rows_to_select = max(1, int(num_rows * 0.5))
        selected_rows = group.head(num_rows_to_select)  # Select the first 50% smallest rows
        return selected_rows


    # # Import Databases

    # In[27]:


    df_base = pd.read_csv('base.csv', sep=";")
    df_airports = pd.DataFrame.from_dict(airportsdata.load(), orient='index')
    df_airports[['lat', 'lon']] = df_airports[['lat', 'lon']].astype(float)


    # # Transform data to pd.DataFrame

    # In[28]:


    df_base['arr_origin'] = input_dict['arr_origin']
    df_base['arr_destination'] = input_dict['arr_destination']
    df_base['date'] = input_dict['date']
    df_base['payload_kg'] = input_dict['payload']
    df_base['num_flights'] = (df_base['payload_kg'] / df_base['MZFW_Payload']).apply(np.ceil).astype(int)

    if input_dict['cargo_items'] and len(input_dict['cargo_items']) > 0:
      df_base['w_1'] = int(input_dict['cargo_items'][0]['w'])
      df_base['h_1'] = int(input_dict['cargo_items'][0]['h'])
      df_base['l_1'] = int(input_dict['cargo_items'][0]['l'])
    else:
      df_base['w_1'] = 0
      df_base['h_1'] = 0
      df_base['l_1'] = 0


    # # Drop Oversize

    # In[29]:


    # Rule 1: Item should be lower by Width of one of the Doors
    df_base = df_base[(df_base['w_1'] < df_base['nose_door_w']) |
                    (df_base['w_1'] < df_base['main_deck_side_door_w']) |
                    (df_base['w_1'] < df_base['main_deck_side_FWD_door_w']) |
                    (df_base['w_1'] < df_base['main_deck_side_AFT_door_w'])]

    # Rule 2: Item should be lower by Height of one of the Doors
    df_base = df_base[(df_base['h_1'] < df_base['nose_door_h']) |
                    (df_base['h_1'] < df_base['main_deck_side_door_h']) |
                    (df_base['h_1'] < df_base['main_deck_side_FWD_door_h']) |
                    (df_base['h_1'] < df_base['main_deck_side_AFT_door_h'])]

    # Rule 3: Item should be lower by Lenght of one of the Doors
    df_base = df_base[(df_base['l_1'] < df_base['main_compartment_l']) |
                    (df_base['l_1'] < df_base['lower_FWD_compartment_l']) |
                    (df_base['l_1'] < df_base['lower AFT_compartment_l'])]


    # # Load Coordinates

    # In[30]:



    #--------------

    df_airports_v1 = pd.DataFrame()

    df_airports_v1['arr_origin'] = df_airports['iata']
    df_airports_v1['dep_airport_lat'] = df_airports['lat']
    df_airports_v1['dep_airport_long'] = df_airports['lon']

    df_base = df_base.merge(df_airports_v1, on='arr_origin', how='left')

    #--------------

    df_airports_v2 = pd.DataFrame()

    df_airports_v2['arr_destination'] = df_airports['iata']
    df_airports_v2['arr_airport_lat'] = df_airports['lat']
    df_airports_v2['arr_airport_long'] = df_airports['lon']

    df_base = df_base.merge(df_airports_v2, how='left', on='arr_destination')


    # # Load Distances

    # In[31]:


    df_base['flight_distance'] = df_base.apply(lambda row: distance(row.dep_airport_lat, row.dep_airport_long, row.arr_airport_lat, row.arr_airport_long) , axis = 1)
    df_base['empty_distance'] = df_base['flight_distance']

    df_base['ferry_1_virtual_distance'] = df_base.apply(lambda row: distance(row.virtual_base_lat, row.virtual_base_long, row.dep_airport_lat, row.dep_airport_long) , axis = 1)
    df_base['ferry_1_current_distance'] = df_base.apply(lambda row: distance(row.current_location_lat, row.current_location_long, row.dep_airport_lat, row.dep_airport_long) , axis = 1)

    df_base['ferry_2_distance'] = df_base.apply(lambda row: distance(row.arr_airport_lat, row.arr_airport_long, row.virtual_base_lat, row.virtual_base_long) , axis = 1)


    # # Flight

    # In[32]:


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

    # In[33]:


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

    # In[34]:


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

    # In[35]:


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

    # In[36]:


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

    # In[37]:


    # Time
    df_base['flight_time'] = df_base['flight_time']
    df_base['empty_time'] = df_base['empty_time']
    df_base['ferry_time'] = np.minimum(df_base['ferry_1_virtual_time'], df_base['ferry_1_current_time'])  + df_base['ferry_2_time']

    # Time Totals
    df_base['total_time'] = df_base['flight_time'] + df_base['empty_time'] + df_base['ferry_time']
    df_base['total_ferry_time'] = df_base['empty_time'] + df_base['ferry_time']

    # Cost
    df_base['flight_cost'] = df_base['flight_cost']
    df_base['empty_cost'] = df_base['empty_cost']
    df_base['ferry_cost'] = np.minimum(df_base['ferry_1_virtual_cost'], df_base['ferry_1_current_cost']) + df_base['ferry_2_cost']
    df_base['total_cost'] = df_base['flight_cost'] + df_base['empty_cost'] + df_base['ferry_cost']

    # Margin
    df_base['margin_h'] = df_base.apply(lambda row: m(row.total_time, row.a_margin, row.b_margin, row.c_margin, row.d_margin) if m(row.total_time, row.a_margin, row.b_margin, row.c_margin, row.d_margin) > 0 else 3.00, axis=1)

    # Price
    df_base['price'] = df_base['total_cost'] * (1+df_base['margin_h'])

    # -----------

    # Drop nan in DataFrame
    df_base = df_base.dropna(subset='price')

    # Sort the DataFrame by 'price' in ascending order
    df_base_sorted = df_base.sort_values(by='price')

    # Group the sorted DataFrame by 'operator' and 'Category'
    grouped = df_base_sorted.groupby(['operator', 'Category'])

    # Apply the function to each group
    df_selected = grouped.apply(select_smallest)
    df_selected = df_selected.sort_values(by='price')
    df_selected = df_selected.reset_index(drop=True)

    df_average_price = df_selected.groupby(['operator', 'Category'])['price'].mean().reset_index()

    df_unique = df_selected.drop_duplicates(subset=['operator', 'Category'])
    df_unique = df_unique.reset_index(drop=True)
    df_unique = df_unique.drop('price', axis=1)

    df_merged = pd.merge(df_unique, df_average_price, on=['operator', 'Category'], how='left')
    df_base = df_merged

    # -----------

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
    df_output['Position Time'] = np.minimum(df_base['ferry_1_virtual_time'], df_base['ferry_1_current_time'])
    df_output['Position Time'] = df_output['Position Time'].apply(lambda x: '({1}h {0}min Pos.)'.format(round((x % 1)*60), round((x - (x % 1)))))
    df_output['Flight Time'] = df_base['flight_time']
    df_output['Flight Time'] = df_output['Flight Time'].apply(lambda x: '{1}h {0}min'.format(round((x % 1)*60), round((x - (x % 1)))))
    df_output['Number of Flights'] = df_base['num_flights'].apply(lambda x: '{} leg'.format(x))
    df_output['Payload m3'] = df_base['Volume']
    df_output['Payload kg'] = df_base['MZFW_Payload']
    df_output['Price'] = df_base['price']
    df_output['Price'] = df_output['Price'].apply(lambda x: "{:,.0f} USD".format((x)))

    df_output['Email'] = df_base['email']
    df_output['Phone'] = df_base['phone']
    df_output['Website'] = df_base['link']
    df_output['Form'] = df_base['form']


    # dict_output
    dict_output_time_critical = df_output.to_dict('records')

    dict_output_time_critical


    # # General quotations

    # In[39]:


    # Time
    df_base['flight_time'] = df_base['flight_time']
    df_base['empty_time'] = df_base['empty_time']
    df_base['ferry_time'] = df_base['ferry_1_virtual_time'] + df_base['ferry_2_time']

    # Time Totals
    df_base['total_time'] = df_base['flight_time'] + df_base['empty_time'] + df_base['ferry_time']
    df_base['total_ferry_time'] = df_base['empty_time'] + df_base['ferry_time']

    # Cost
    df_base['flight_cost'] = df_base['flight_cost']
    df_base['empty_cost'] = df_base['empty_cost']
    df_base['ferry_cost'] = df_base['ferry_1_virtual_cost'] + df_base['ferry_2_cost']
    df_base['total_cost'] = df_base['flight_cost'] + df_base['empty_cost'] + df_base['ferry_cost']

    # Margin
    df_base['margin_h'] = df_base.apply(lambda row: m(row.total_time, row.a_margin, row.b_margin, row.c_margin, row.d_margin) if m(row.total_time, row.a_margin, row.b_margin, row.c_margin, row.d_margin) > 0 else 3.00, axis=1)

    # Price
    df_base['price'] = df_base['total_cost'] * (1+df_base['margin_h'])

    # -----------

    # Drop nan in DataFrame
    df_base = df_base.dropna(subset='price')

    # Sort the DataFrame by 'price' in ascending order
    df_base_sorted = df_base.sort_values(by='price')

    # Group the sorted DataFrame by 'operator' and 'Category'
    grouped = df_base_sorted.groupby(['operator', 'Category'])

    # Apply the function to each group
    df_selected = grouped.apply(select_smallest)
    df_selected = df_selected.sort_values(by='price')
    df_selected = df_selected.reset_index(drop=True)

    df_average_price = df_selected.groupby(['operator', 'Category'])['price'].mean().reset_index()

    df_unique = df_selected.drop_duplicates(subset=['operator', 'Category'])
    df_unique = df_unique.reset_index(drop=True)
    df_unique = df_unique.drop('price', axis=1)

    df_merged = pd.merge(df_unique, df_average_price, on=['operator', 'Category'], how='left')
    df_base = df_merged

    # -----------

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
    df_output['Position Time'] = df_base['ferry_1_virtual_time']
    df_output['Position Time'] = df_output['Position Time'].apply(lambda x: '({1}h {0}min Pos.)'.format(round((x % 1)*60), round((x - (x % 1)))))
    df_output['Flight Time'] = df_base['flight_time']
    df_output['Flight Time'] = df_output['Flight Time'].apply(lambda x: '{1}h {0}min'.format(round((x % 1)*60), round((x - (x % 1)))))
    df_output['Number of Flights'] = df_base['num_flights'].apply(lambda x: '{} leg'.format(x))
    df_output['Payload m3'] = df_base['Volume']
    df_output['Payload kg'] = df_base['MZFW_Payload']
    df_output['Price'] = df_base['price']
    df_output['Price'] = df_output['Price'].apply(lambda x: "{:,.0f} USD".format((x)))

    df_output['Email'] = df_base['email'].fillna('') if not df_base['email'].empty else df_base['email']
    df_output['Phone'] = df_base['phone'].fillna('') if not df_base['phone'].empty else df_base['phone']
    df_output['Website'] = df_base['link'].fillna('') if not df_base['link'].empty else df_base['link']
    df_output['Form'] = df_base['form'].fillna('') if not df_base['form'].empty else df_base['form']

    # dict_output
    dict_output_general = df_output.to_dict('records')[0:13]
    return dict_output_general


    # In[ ]:




