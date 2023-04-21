#!/usr/bin/env python
# coding: utf-8

# In[68]:


# import packages


# In[69]:


import pandas as pd
import numpy as np
import datetime as dt
import haversine as hs


# In[70]:


# define input dictionary


# In[71]:


input_dict = {'arr_origin': 'FRA', 'arr_destination': 'BER', 'date': '30/03/2023', 'payload': 100}


# In[72]:


# import databases


# In[73]:


df_types = pd.read_excel('ac_types.xlsx')
df_airports = pd.read_csv('airport-codes_csv.csv')
df_airports[['longitude_deg', 'latitude_deg']] = df_airports.coordinates.str.split(",", expand = True).astype(float)


# In[74]:


# transform data to working table


# In[75]:


df_types['arr_origin'] = input_dict['arr_origin']
df_types['arr_destination'] = input_dict['arr_destination']
df_types['date'] = input_dict['date']
df_types['payload'] = input_dict['payload']
df_types['num_flights'] = (df_types['payload'] / df_types['ac_payload']).apply(np.ceil).astype(int)


# In[76]:


# calculate flying time and cost for aircraft option


# In[77]:


df_airports_v1 = pd.DataFrame()

df_airports_v1['arr_origin'] = df_airports['iata_code']
df_airports_v1['dep_airport_lat'] = df_airports['latitude_deg']
df_airports_v1['dep_airport_long'] = df_airports['longitude_deg']

df_types = df_types.merge(df_airports_v1, on='arr_origin', how='left')

#--------------

df_airports_v2 = pd.DataFrame()

df_airports_v2['arr_destination'] = df_airports['iata_code']
df_airports_v2['arr_airport_lat'] = df_airports['latitude_deg']
df_airports_v2['arr_airport_long'] = df_airports['longitude_deg']

df_types = df_types.merge(df_airports_v2, how='left', on='arr_destination')

#--------------

df_airports_v3 = pd.DataFrame()

df_airports_v3['base'] = df_airports['iata_code']
df_airports_v3['base_airport_lat'] = df_airports['latitude_deg']
df_airports_v3['base_airport_long'] = df_airports['longitude_deg']

df_types = df_types.merge(df_airports_v3, how='left', on='base')

#--------------

df_types['flight_distance'] = df_types.apply(lambda row: hs.haversine((row.dep_airport_lat, row.dep_airport_long),(row.arr_airport_lat, row.arr_airport_long)) , axis = 1)

df_types['ferry_distance_1'] = df_types.apply(lambda row: hs.haversine((row.base_airport_lat, row.base_airport_long),(row.dep_airport_lat, row.dep_airport_long)) , axis = 1)

df_types['ferry_distance_2'] = df_types.apply(lambda row: hs.haversine((row.arr_airport_lat, row.arr_airport_long),(row.base_airport_lat, row.base_airport_long)) , axis = 1)

df_types['flight_time'] = df_types['flight_distance'] / df_types['speed'] * df_types['num_flights']

df_types['ferry_time'] = df_types['ferry_distance_1'] / df_types['speed'] + df_types['ferry_distance_2'] / df_types['speed'] + df_types['flight_distance'] / df_types['speed'] * (df_types['num_flights'] - 1)

df_types['total_price'] = df_types['flight_time'] * df_types['price'] + df_types['ferry_time'] * df_types['price'] / 2

df_types = df_types.sort_values(by=['total_price']).reset_index(drop=True)


# In[78]:


# creating final table


# In[79]:


df_output = pd.DataFrame()

df_output['DEP'] = df_types['arr_origin']
df_output['ARR'] = df_types['arr_destination']
df_output['Aircraft'] = df_types['ac_type_text']
df_output['Number of Flights'] = df_types['num_flights']
df_output['Total Flight Time'] = df_types['flight_distance'] / df_types['speed'] * (df_types['num_flights'] * 2 - 1)
df_output['Total Flight Time'] = df_output['Total Flight Time'].apply(lambda x: '{1}h {0}m'.format(round((x % 1)*60), round((x - (x % 1)))))


df_output['Total Price'] = df_types['total_price']
df_output['Total Price'] = df_output['Total Price'].apply(lambda x: "EUR {:,.0f}".format((x)))


# In[80]:


# convert dataframe to list of dictionaries


# In[81]:


output_dict = df_output.to_dict('records')


# In[82]:


print(output_dict)

