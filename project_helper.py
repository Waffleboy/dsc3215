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
working_directory = "/storage/NUS_STUFF/LectureTutorials/IVLE/DSC3215/"
# filepath to the raw data csv
dsc_data_filename = "dsc_data.csv"
formatted_csv_filename = "formatted_dsc_data.csv"
countries = ['Singapore','United States','India','Canada']
# for simulated
countries = {'Singapore':{"mean":334,"sd":100},
            'United States':{"mean":350,"sd":110},
            'India':{"mean":700,"sd":300},
            'Canada':{"mean":300,"sd":90}
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
        temp_df["sales"] = scipy.stats.norm.rvs(loc=countries[country]["mean"],scale = countries[country]["sd"],size=366)
        temp_df["sales"][temp_df["sales"] <0] = 0 #no negative sales
        lst.append(temp_df)
    df = pd.concat(lst)
    return df


# Convert the Tableau Data to 4 countries by year instead.

def convert_tableau_data_to_dsc(data_df,save=False):
    global working_directory,formatted_csv_filename,countries
    selected_cols = ['sales','country','order_date']
    data["Order Date"] = pd.to_datetime(data["Order Date"])
    # convert all to 2016.
    data["Order Date"] = data["Order Date"].map(lambda x: datetime.date(2016,x.month,x.day))
    available_years = list(set([x.year for x in data["Order Date"]]))
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
# run
#==============================================================================
if __name__ == '__main__':
    data = pd.read_csv(working_directory + dsc_data_filename)
    df = pd.read_csv(working_directory+dsc_data_filename)
    df = convert_tableau_data_to_dsc(df,True)