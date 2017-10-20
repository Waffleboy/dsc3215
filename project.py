#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 00:56:45 2017

Inventory Model Solver

@author: thiru
"""
import scipy.stats
import scipy.integrate
import os
import pandas as pd
import datetime
import math

#==============================================================================
#                               Initial Settings
#==============================================================================
working_directory = "/storage/NUS_STUFF/LectureTutorials/IVLE/DSC3215/project/"
# Run helper if you dont have this.
dsc_data_filename = "formatted_dsc_data.csv"
dsc_data_settings = "dsc_data_settings.csv"

#==============================================================================
#                                 Helper Functions
#==============================================================================

def calculate_optimal_order_probability(price, cost, holding_cost, shortage_penalty):
    return (price+shortage_penalty-cost) / (price+shortage_penalty+holding_cost)

def cdf_normal_dist(x):
    return scipy.stats.norm.ppf(x)

def cdf_uniform_dist(x):
    return scipy.stats.uniform.cdf(x)

def calculate_optimal_order_quantity(mean,variance,probability,distribution='normal'):
    return "({} - x)+".format(calculate_optimal_order_up_to_point(mean,variance,probability,distribution))

# no leadtime
def calculate_optimal_order_up_to_point(mean,variance,probability,distribution='normal'):
    if distribution == 'normal':
        return mean + ((variance)**(1/2))*cdf_normal_dist(probability)

def calculate_optimal_order_up_to_point_leadtime(days,mean,variance,probability,distribution='normal'):
    if distribution == 'normal':
        return round((days)*mean + math.sqrt(days)*(variance**(1/2)) * cdf_normal_dist(probability),2)


def calculate_optimal_profit(w,price,cost,holding_cost,shortage_penalty):
    integral_value, error = scipy.integrate.quad(loss_function,w,scipy.inf)
    profit = (holding_cost+cost)*w + (price+holding_cost+shortage_penalty)*integral_value
    return profit


def calculate_fixed_cost_optimal_qty(K,mean,variance,price,cost,holding_cost,shortage_penalty,leadtime=0):
    global probability_value
    actual_leadtime = leadtime+ 1 #his n+1 rule
    sd = variance**(1/2)
    probability = calculate_optimal_order_probability(price, cost, holding_cost, shortage_penalty)
    if leadtime:
        optimal_order_point = calculate_optimal_order_up_to_point_leadtime(actual_leadtime,mean,variance,probability)
    else:
        optimal_order_point = calculate_optimal_order_up_to_point(mean,variance,probability)

    w_star = (optimal_order_point - (actual_leadtime*mean)) / ((actual_leadtime**(1/2))*sd)
    probability_value = w_star  #quick hack

    # compute RHS of that equation
    if leadtime:
        rhs = K / ((actual_leadtime**(1/2))*sd)
    else:
        rhs = K / sd

    # compute Profit(s)
    profit_s = calculate_optimal_profit(w_star,price,cost,holding_cost,shortage_penalty)

    # shift all to the right
    rhs = rhs + profit_s

    # compute Profit(mew + sd(w_star)) (find first negative)
    error = 0.01
    w = w_star
    probability_value = w
    lhs = calculate_optimal_profit(w,price,cost,holding_cost,shortage_penalty)
    while abs(lhs - rhs) > error:
        w -= 0.0001
        probability_value = w
        lhs = calculate_optimal_profit(w,price,cost,holding_cost,shortage_penalty)

    # recompute proper profit - EDDY FIX THIS PLEASE
#    if leadtime:
#        profit_s = actual_leadtime**(1/2) * sd * calculate_optimal_profit(w_star,price,cost,holding_cost,shortage_penalty)
#        profit_mew_sd = actual_leadtime**(1/2) * sd * calculate_optimal_profit(w,price,cost,holding_cost,shortage_penalty)
#    else:
#        profit_s =  sd * calculate_optimal_profit(w_star,price,cost,holding_cost,shortage_penalty)
#        profit_mew_sd = sd * calculate_optimal_profit(w,price,cost,holding_cost,shortage_penalty)

    # optimal re order point:
    if leadtime:
        optimal_re_order =  w*(actual_leadtime**(1/2))*sd + actual_leadtime*mean
    else:
        optimal_re_order = mean + w*sd

    ## round everything to 2dp
    #profit_mew_sd,profit_s= round(profit_mew_sd,2),round(profit_s,2)
    optimal_re_order,optimal_order_point  = round(optimal_re_order,2),round(optimal_order_point,2)

    print("For Leadtime: {}".format(leadtime))
    print("With fixed cost K of ${} USD:".format(K))
    print("Optimal Re Order Point: {}".format(optimal_re_order))
    print("Optimal Order Up to Level: {}".format(optimal_order_point))
    print('\n')
    return optimal_re_order,optimal_order_point

def loss_function(x):
    global probability_value #quick hack
    return (x-probability_value)*(1/(math.sqrt(2*math.pi)))*math.e**(-1*((x**2)/2))

#==============================================================================
#                                   Run
#==============================================================================
df = pd.read_csv(working_directory+dsc_data_filename)
settings_df = pd.read_csv(working_directory+dsc_data_settings)
settings_df.index = settings_df["Country"]
del settings_df["Country"]
countries = list(df["country"].unique())

for country in countries:
    print("-"*7 + "For {}".format(country) + '-'*7)
    df_subset = df[df["country"] == country]
    settings_row = settings_df[settings_df.index == country].to_dict('records')[0]
    sales_mean = df["sales"].mean()
    sales_variance = df["sales"].var()

    price = settings_row["Unit Sale Price"]
    cost = settings_row["Unit Order Cost"]
    holding_cost = settings_row["Unit Holding Cost"]
    shortage_penalty = settings_row["Unit Shortage Penalty"]
    fixed_order_cost = settings_row["Fixed Order Cost"]
    leadtime = settings_row["Leadtime (Days)"]

    probability = calculate_optimal_order_probability(price,cost,holding_cost,shortage_penalty)
    # assuming normal, zero lead time
    optimal_order_upto_point = calculate_optimal_order_up_to_point(sales_mean,sales_variance,probability)
    optimal_re_order,_ =  calculate_fixed_cost_optimal_qty(fixed_order_cost,sales_mean,sales_variance,price,cost,holding_cost,shortage_penalty)

    # assuming normal, leadtime given.
    optimal_order_upto_point_leadtime = calculate_optimal_order_up_to_point_leadtime(leadtime,sales_mean,sales_variance,probability)
    optimal_re_order_leadtime,_ =  calculate_fixed_cost_optimal_qty(fixed_order_cost,sales_mean,sales_variance,price,cost,holding_cost,shortage_penalty,leadtime)
