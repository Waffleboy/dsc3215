#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 17:03:21 2017

@author: thiru
"""
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns


#==============================================================================
#                               Initial Settings
#==============================================================================
working_directory = "/storage/NUS_STUFF/LectureTutorials/IVLE/DSC3215/project/"
# Run helper if you dont have this.
dsc_data_filename = "formatted_dsc_data.csv"
dsc_data_settings = "dsc_data_settings.csv"

def obtain_probability_dist(column):
    column = column.map(lambda x:int(x))
    counts = column.value_counts()
    counts = counts / len(counts) # obtain probability
    counts_dict_form = counts.to_dict()
    return counts_dict_form


df = pd.read_csv(dsc_data_filename)
df["sales"] = df["sales"].map(lambda x:int(x))
unique_countries = df["country"].unique()
settings_df = pd.read_csv(working_directory+dsc_data_settings)
settings_df.index = settings_df["Country"]
del settings_df["Country"]

def calculate_holding_cost(holding_cost,order_quantity,demand,demand_probability):
    hold_quantity = (order_quantity - demand)
    if hold_quantity <= 0:
        return 0
    return hold_quantity*holding_cost * demand_probability

def calculate_shortage_cost(shortage_penalty,order_quantity,demand,demand_probability):
    shortage_quantity = demand - order_quantity
    if shortage_quantity <= 0:
        return 0
    return shortage_penalty * shortage_quantity * demand_probability


for country in unique_countries:
    settings_row = settings_df[settings_df.index == country].to_dict('records')[0]
    country_df = df[df["country"] == country]
    prob_dist = obtain_probability_dist(country_df["sales"])
    min_demand = min(country_df["sales"])
    max_demand = max(country_df["sales"])

    price = settings_row["Unit Sale Price"]
    cost = settings_row["Unit Order Cost"]
    holding_cost = settings_row["Unit Holding Cost"]
    shortage_penalty = settings_row["Unit Shortage Penalty"]
    fixed_order_cost = settings_row["Fixed Order Cost"]
    leadtime = settings_row["Leadtime (Days)"]


    order_quantity_range = [x for x in range(1,max_demand+1)]

    #O(n^2) loop
    order_quantity_array = []
    for order_quantity in order_quantity_range:
        temp = []
        for demand in order_quantity_range:
            try:
                demand_probability = prob_dist[demand]
            except:
                demand_probability = 0
            profit = demand*price*demand_probability - cost*order_quantity - calculate_holding_cost(holding_cost,order_quantity,demand,demand_probability) - calculate_shortage_cost(shortage_penalty,order_quantity,demand,demand_probability)
            temp.append([demand,profit])
        total_profit_for_current_order_quantity = sum([x[1] for x in temp])
        order_quantity_array.append([order_quantity,total_profit_for_current_order_quantity])

    plt.plot([x[0] for x in order_quantity_array],[x[1] for x in order_quantity_array])

