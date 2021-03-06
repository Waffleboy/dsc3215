#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 17:03:21 2017

@author: thiru
"""
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np

#==============================================================================
#                               Initial Settings
#==============================================================================
working_directory = "/storage/NUS_STUFF/LectureTutorials/IVLE/DSC3215/project/"
#working_directory = "/Users/jingyu/Dropbox/DSC3215/dsc3215/"
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


    #order_quantity_range = [x for x in range(1,max_demand+1)]
    order_quantity_range = [x for x in range(1,max_demand*2)]

    #O(n^2) loop
    order_quantity_array = []
    for order_quantity in order_quantity_range:
        temp = []

        #for demand in order_quantity_range:
        for demand in range(min_demand, max_demand+1):
            try:
                demand_probability = prob_dist[demand]
            except:
                continue

            # check if order_quantity < demand (revenue will be order_qty*price instead of demand*price)
            if demand <= order_quantity:
                #profit = demand*price*demand_probability - cost*order_quantity - calculate_holding_cost(holding_cost,order_quantity,demand,demand_probability) - calculate_shortage_cost(shortage_penalty,order_quantity,demand,demand_probability)
                profit = demand*price*demand_probability - cost*order_quantity*demand_probability - calculate_holding_cost(holding_cost,order_quantity,demand,demand_probability) - calculate_shortage_cost(shortage_penalty,order_quantity,demand,demand_probability)
                temp.append([demand,profit])
            else:
                #profit = order_quantity*price*demand_probability - cost*order_quantity - calculate_holding_cost(holding_cost,order_quantity,demand,demand_probability) - calculate_shortage_cost(shortage_penalty,order_quantity,demand,demand_probability)
                profit = order_quantity*price*demand_probability - cost*order_quantity*demand_probability - calculate_holding_cost(holding_cost,order_quantity,demand,demand_probability) - calculate_shortage_cost(shortage_penalty,order_quantity,demand,demand_probability)
                temp.append([demand,profit])

        total_profit_for_current_order_quantity = sum([x[1] for x in temp])
#        if fixed_order_cost:
#            total_profit_for_current_order_quantity -= fixed_order_cost
        order_quantity_array.append([order_quantity,total_profit_for_current_order_quantity])

    max_point = max(order_quantity_array,key =lambda x:x[1])
    dup_list = sorted(order_quantity_array, key = lambda x:x[1])
    text_x_axis = max_point[0] + 20
    text_y_axis = dup_list[30][1]
    formatted_profit = round(max_point[1],2)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # Maybe we should plot one for each country instead?
    ax.plot([x[0] for x in order_quantity_array],[x[1] for x in order_quantity_array])
    ax.set_ylabel('Profit in $USD')
    ax.set_xlabel('Order Quantity')
    ax.set_title('Profit Curve for {}'.format(country))

    if fixed_order_cost:
        new_y = max_point[1] - fixed_order_cost
        #find reorder point
        reorder_idx = 0
        for i in range(max_point[0],0,-1):
            if max_point[1] -  order_quantity_array[i][1] > fixed_order_cost:
                reorder_idx = i
                break
        reorder_point = order_quantity_array[reorder_idx][0]

        ax.axhline(y=new_y,linestyle='--')
        ax.text(x=0.02,y=0.4,s="Reorder\nQuantity: {}".format(reorder_point),transform = ax.transAxes,fontsize=14)

    ax.axvline(x=max_point[0],linestyle='--')
    ax.text(0.37, 0.2,"Profit: ${}\n\nOrder Up To Quantity: {}".format(formatted_profit,max_point[0]),verticalalignment='bottom', transform = ax.transAxes,horizontalalignment='left',fontsize=15)
    plt.show()