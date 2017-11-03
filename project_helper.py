#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 01:36:36 2017

@author: thiru
"""
import scipy.stats
import os
import pandas as pd
import datetime

#==============================================================================
#                               Initial Settings
#==============================================================================
working_directory = "/storage/NUS_STUFF/LectureTutorials/IVLE/DSC3215/project/"
# filepath to the raw data csv
dsc_data_filename = "dsc_data.csv"
formatted_csv_filename = "formatted_dsc_data.csv"
countries = ['Singapore','United States','India','Canada']
# for simulated
countries = {'Singapore':{"mean":334.65,"sd":97.58},
            'United States':{"mean":350.88,"sd":107.98},
            'India':{"mean":700.287,"sd":300.985},
            'Canada':{"mean":300.29,"sd":90.728}
            }


#==============================================================================
#                            Misc functions
#==============================================================================

def generate_own_data(countries):
    lst = []
    for country in countries:
        temp_df = pd.DataFrame(index=[x for x in range(366)])
        temp_df["country"] = country
        temp_df["date"] = list(pd.date_range(start='01-01-2016',end='31-12-2016'))
        print(country)
        temp_df["sales"] = scipy.stats.norm.rvs(loc=countries[country]["mean"],scale = countries[country]["sd"],size=366)
        temp_df["sales"][temp_df["sales"] <0] = 0 #no negative sales
        lst.append(temp_df)
    df = pd.concat(lst,axis=0)
    df = df.reset_index()
    return df


# Convert the Tableau Data to 4 countries by year instead.

def convert_tableau_data_to_dsc(data_df,save=False):
    global working_directory,formatted_csv_filename,countries
    selected_cols = ['sales','country','order_date']
    data_df["Order Date"] = pd.to_datetime(data_df["Order Date"])
    # convert all to 2016.
    data_df["Order Date"] = data_df["Order Date"].map(lambda x: datetime.date(2016,x.month,x.day))
    available_years = list(set([x.year for x in data_df["Order Date"]]))
    available_years.sort() #keep consistent
    lst = []
    for i in range(len(available_years)):
        current_year = available_years[i]
        current_country = countries[i]
        msk = (data["Order Date"] >= datetime.date(year=current_year,month=1,day=1)) &  (data["Order Date"] < datetime.date(year=current_year+1,month=1,day=1))
        temp_df = data[msk]
        temp_df["country"] = current_country
        temp_df['order_date'] = temp_df['Order Date']
        temp_df['sales'] = temp_df["Sales"]
        # remove all useless columns
        temp_df = temp_df[selected_cols]
        lst.append(temp_df)
    df = pd.concat(lst,axis=0)
    if save:
        save_dataframe(df,working_directory+formatted_csv_filename)
    return df

def save_dataframe(df,working_directory):
    df.to_csv(working_directory,index=False)

#==============================================================================
# Plot fake data
#==============================================================================
import seaborn as sns
def plot():
    global working_directory,formatted_csv_filename
    df = pd.read_csv(working_directory+formatted_csv_filename)
    countries = list(df["country"].unique())
    for country in countries:
        current_country_df = df[df["country"] == country]
        sales = current_country_df["sales"]
        ax = sales.plot('hist',bins=13,title = "Sales Histogram for {}".format(country),legend=True)
        ax.set_xlabel("Sales in $USD")
    L=ax.legend()
    for i in range(len(L)):
       entry.set_text(countries[i])

def plot_cdf():
    import pylab as pl
    global working_directory,formatted_csv_filename
    df = pd.read_csv(working_directory+formatted_csv_filename)
    countries = list(df["country"].unique())
    for country in countries:
        current_country_df = df[df["country"] == country]
        sales = current_country_df["sales"]
        ax = sales.hist(cumulative=True,normed=True)
        ax.set_xlabel("Sales Quantity")
        ax.set_title("CDF of demand for {}".format(country))

def plot_profit_curve():
    global working_directory,formatted_csv_filename
    df = pd.read_csv(working_directory+formatted_csv_filename)
    dsc_data_settings = "dsc_data_settings.csv"
    settings_df = pd.read_csv(working_directory+dsc_data_settings)
    settings_df.index = settings_df["Country"]
    del settings_df["Country"]
    countries = list(df["country"].unique())
    for country in countries:
        settings_row = settings_df[settings_df.index == country].to_dict('records')[0]
        price = settings_row["Unit Sale Price"]
        cost = settings_row["Unit Order Cost"]
        holding_cost = settings_row["Unit Holding Cost"]
        shortage_penalty = settings_row["Unit Shortage Penalty"]

        height = []
        x_axis = []
        current_country_df = df[df["country"] == country]
        bin_count = 100
        increments = max(current_country_df["sales"]) / bin_count
        curr_cumulative_count = increments
        for i in range(bin_count):
            sub_df = current_country_df["sales"][current_country_df["sales"] <= curr_cumulative_count]
            height.append(len(sub_df))
            x_axis.append(curr_cumulative_count)
            curr_cumulative_count += increments

        height = [x / max(height) for x in height]

        constant = -1*cost + price + shortage_penalty
        constant2 =  (price + shortage_penalty + holding_cost)
        profit_y = [(constant - constant2*x) for x in height]
        plt.plot(x_axis,profit_y)


#==============================================================================
# run
##==============================================================================
#if __name__ == '__main__':
#    data = pd.read_csv(working_directory + dsc_data_filename)
#    df = pd.read_csv(working_directory+dsc_data_filename)
#    df = convert_tableau_data_to_dsc(df,True)