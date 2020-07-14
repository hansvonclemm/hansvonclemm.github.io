#!/usr/bin/env python
# coding: utf-8

# ## SensibleHeat Storage Volume Analysis
# 
# The basic and simplified model used to estimate the tank size required for different parts of the United States is built off of a dataset provided by OpenEI. 
# 
# [OpenEI](https://openei.org/doe-opendata/dataset/commercial-and-residential-hourly-load-profiles-for-all-tmy3-locations-in-the-united-states) created a detailed (hourly) load profile for TMY3 locations in the United States.
# 
# There is data for both residential and commercial building types, but here we only look at residential, which is broken into two load categories, HIGH and LOW. The United States is broken up into five Climate Zones, each of which is given a different type of building for decent assumptions to be made. Assumptions are broken down below: 
# 
# ### Climate Zones
# ![](climateZ.png)
# ### High Load Characteristics
# ![](highLoad.png)
# ### Low Load Characteristics
# ![](lowLoad.png)
# 
# ### Data
# For the sake of simplicity, I've cleaned up and brought over heating and domestic hot water data from a handful of TMY3 Loactions, representative of the USA. 
# 
# 'Cleaning up data' consisted of summing loads on a 24 hour cylce and retrieving the max. Units are a mess. Apologies.
# 
# You may manipulate the script however you'd like, but there isn't much here... Tweak the parameters and re-run the script to see how storage requirements change.

# In[2]:


import os
import pandas as pd
import matplotlib.pyplot as plt
from array import *
import plotly.graph_objects as go


    


# In[3]:


# PARAMETERS FOR ADJUSTMENT
storage_Temp = 150 #[F]
room_Temp = 70 #[F]
standby_losses = 5 # [%] daily
NG_efficiency = 90 # [%] 90% efficient furnace

# GLOBAL VARIABLES
c_p = 4.186 #[kJ/kg]
storage_time = 24 #[hrs]
to_kBTU = 3.41214


# In[4]:


# FUNCTIONS 

def calcVol(kW):
    tr = (room_Temp-32) * (5/9)
    ts = (storage_Temp-32) * (5/9)
    delta_T = ts-tr
    m = (kW*3600) / (c_p * delta_T) * ((100-standby_losses)/NG_efficiency)
    
    return(m/1000)


# In[5]:


openEI_df = pd.read_csv('OpenEI_loads.csv')
openEI_df['storage_LOW[m3]'] = calcVol(openEI_df['heat_Need_LOW[kWh]'])
openEI_df['storage_HIGH[m3]'] = calcVol(openEI_df['heat_Need_HIGH[kWh]'])
openEI_df['avgLoad_LOW[kW]'] = openEI_df['heat_Need_LOW[kWh]'] / storage_time
openEI_df['avgLoad_HIGH[kW]'] = openEI_df['heat_Need_HIGH[kWh]'] / storage_time


# In[6]:


openEI_df


# In[ ]:





# In[7]:


# Plot Storage Required By Location as Bar Graph

cities = openEI_df['city'].to_list()
gal_low = (openEI_df['storage_LOW[m3]']*264).to_list()
gal_hi = (openEI_df['storage_HIGH[m3]']*264).to_list()
fig = go.Figure()
fig.add_trace(go.Bar(
    x=cities,
    y=gal_low,
    name='LOW LOAD storage',
    marker_color='indianred'
))
fig.add_trace(go.Bar(
    x=cities,
    y=gal_hi,
    name='HIGH LOAD storage',
    marker_color='lightsalmon'
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(yaxis_title ='gallons', title='VOLUME NEEDED TO FULLY SHIFT 24 HOUR LOAD', barmode='group', xaxis_tickangle=-45)
fig.show()


# In[8]:


latList = openEI_df['Latitude'].to_list()
lonList = openEI_df['Longitude'].to_list()



mapbox_access_token='pk.eyJ1Ijoia3Bhc2tvIiwiYSI6ImNrMjZrc2tvbjA4ZTczaGxicHRrZWRwYzMifQ.7ZJ4exw5N9ZNYXeHQi8LNg'
fig = go.Figure()
X={
    'latitude':latList,
   'longitude':lonList,
    'gallon':gal_low
}

fig.add_trace(go.Scattermapbox(lat=X['latitude'],lon=X['longitude'],mode='markers', text=X['gallon']))
fig.update_layout(title = 'THERMAL STORAGE VOLUME MAP',hovermode='closest',height=900, mapbox=go.layout.Mapbox(accesstoken=mapbox_access_token, bearing=0,
                                                              center=go.layout.mapbox.Center(lat=40.4,lon=-101.8), pitch=5, zoom=3))
fig.show()

#TODO, SCALE DOTS REALTIVE TO STORAGE QUANTITY


# In[10]:


# Plot the difference in BTU capacity here (use K BTU?) 
# furnace required 
x_axis = ['Boston Low Load', 'Boston High Load']

bostonOnly = openEI_df.loc[openEI_df['city'] == 'Boston-Logan']
low_B = [bostonOnly['peakLoad_LOW[kW]'][2]*to_kBTU, bostonOnly['peakLoad_HIGH[kW]'][2]*to_kBTU]
hi_B = [bostonOnly['avgLoad_LOW[kW]'][2]*to_kBTU, bostonOnly['avgLoad_HIGH[kW]'][2]*to_kBTU]


fig = go.Figure()
fig.add_trace(go.Bar(
    x=x_axis,
    y=low_B,
    name='Peak Load (Capacity Required)',
    marker_color='teal'
))
fig.add_trace(go.Bar(
    x=x_axis,
    y=hi_B,
    name='Avg Load',
    marker_color='mediumaquamarine'
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(yaxis_title = 'kBTU', barmode='group', xaxis_tickangle=-45, title=('HEAT PUMP CAPACITY WITH AND WITHOUT STORAGE'))
fig.show()


# #### Volume
# So it seems preliminary modeling only used baseline load residential conditions, and the high-load residential units will require substantially more storage to fully shift the load. It's worth noting that storage values are for the *coldest* theorhetical day of the year, and thus the unit can continue to fill itself during discharge. That leads to the question of heat pump capacity and 'tank charge' speeds, which is not considered here. 
# 
# Also, the price of storage scales non-linearly with capacity. More storage means less $/gallon
# 
# #### Capacity
# It ends up being that you can address the same load with a heat pump that's 3/4 as big as otherwise necessary. A huge detractor of heat pump technology is their cost, and those savings can offset a large portion of the storage price.
# 
# #### Moooore 
# Not modeled here are the COP and TOU arbitrage gains achieveable through thermal storage. 
# 

# In[ ]:




