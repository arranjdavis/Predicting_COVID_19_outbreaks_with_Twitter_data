#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 10:54:23 2021

@author: arrandavis
"""

from searchtweets import ResultStream, gen_request_parameters, load_credentials
import pandas as pd
from datetime import datetime, timedelta, date
import os
import pickle
import time

############################################################################################################################

### FUNCTIONS ###

#a function for generating hourly times between two time points
def daterange(start_date, end_date):
    delta = timedelta(hours=1)
    while start_date < end_date:
        yield start_date
        start_date += delta

############################################################################################################################

### TWITTER API AUTHENTICATION INFORMATION ###

#change the working directory
os.chdir("../twitter_academic_API_credentials")

#username for the API
username = "@BronwynTarr1"
user_filename = username + '.yaml'

#get the credentials
search_args = load_credentials(user_filename,
                               yaml_key="search_tweets_v2",
                               env_overwrite=True)

#change back the working directory
os.chdir("../code")

############################################################################################################################
        
### SET TWEET COLLECTION DATES AND LOCATIONS ###

#create a date range for the COVID-19 pandemic flu season
flu_2019_begin = date(2019,12,1)
flu_2019_end = date(2020,3,1)
flu_2019 = pd.date_range(flu_2019_begin,flu_2019_end - timedelta(days=1),freq='d').strftime("%Y-%m-%d").to_list()

#create date ranges for the three flu seasons preceding the pandemic
flu_2018_begin = date(2018,12,1)
flu_2018_end = date(2019,3,1)
flu_2018 = pd.date_range(flu_2018_begin,flu_2018_end - timedelta(days=1),freq='d').strftime("%Y-%m-%d").to_list()

flu_2017_begin = date(2017,12,1)
flu_2017_end = date(2018,3,1)
flu_2017 = pd.date_range(flu_2017_begin,flu_2017_end - timedelta(days=1),freq='d').strftime("%Y-%m-%d").to_list()

flu_2016_begin = date(2016,12,1)
flu_2016_end = date(2017,3,1)
flu_2016 = pd.date_range(flu_2016_begin,flu_2016_end - timedelta(days=1),freq='d').strftime("%Y-%m-%d").to_list()

#combine the dates together
all_dates = flu_2016 + flu_2017 + flu_2018 + flu_2019

### ### ###

#create a dictionary of country and language codes for the European countries to collect tweets from
country_codes = {'Germany': 'DE', 
                 'France': 'FR',
                 'Italy': 'IT',
                 'Spain': 'ES',
                 'Poland': 'PL',
                 'Netherlands': 'NL'}

language_codes = {'Germany': 'de', 
                  'France': 'fr',
                  'Italy': 'it',
                  'Spain': 'es',
                  'Poland': 'pl',
                  'Netherlands': 'nl'}

############################################################################################################################

### COLLECT TWEETS ###

#name of file for tracking progress
progress_output = '../progress/dates_collected_eu.txt'

#go through each country in the dictionary
for country in country_codes:
    
    #create the `query` argument to the call to the API for the current day
    query = "-is:retweet " + "(lang:en OR lang:" + language_codes[country] + ") place_country:" + country_codes[country]
    
    #load or create a dictionary to track collection progress (a dataset will be saved for each day for each country)
    try:
        dates_saved = pickle.load(open("../progress/dates_saved_eu.pkl", "rb"))
    except:
        dates_saved = {}
    
    #start the `remaining_days` variable on the day following the last day with saved tweet data
    if country not in dates_saved:
        remaining_days = all_dates
    else:
        last_day_saved = dates_saved[country][-1]
        remaining_days = all_dates[all_dates.index(last_day_saved) + 1:]
        
    #create a wait time variable to be used after the first set of requests
    wait_time = 0 if len(dates_saved) == 0 else 15
        
    #go through each day in the year
    for day in remaining_days:
        print(day)
        
        #track progress
        print("COUNTRY:", country, "| CURRENT DAY:", day, file = open(progress_output, "a"))
        
        #sleep (to avoid rate limit errors, which reset every 15 minutes)
        time.sleep(wait_time*60)
        
        #create a dataframe for the day
        total_day_dat = pd.DataFrame()
        
        #create a list of hourly times for the current day
        date_time_list = []
        start_date = datetime(int(day.split('-')[0]), int(day.split('-')[1]), int(day.split('-')[2]), 0, 00)
        delta = timedelta(days = 1, hours=1)
        end_date = start_date + delta    
        for single_date in daterange(start_date, end_date):
            date_time_list.append(single_date.strftime("%Y-%m-%dT%H:%M:%SZ"))
            
        #go through all the hours in the given day
        for i in range(0, len(date_time_list)):
            if i == len(date_time_list) - 1:
                break
            start_time = date_time_list[i]
            end_time = date_time_list[i + 1]
            
            #set the call to the API (this scrapes - all the tweets in the UK for the given hour - takes less than five minutes minutes)
            rs = ResultStream(request_parameters={"query": query,
                                                  "start_time": start_time,
                                                  "end_time": end_time,
                                                  "max_results": "500",
                                                  "expansions": "author_id,geo.place_id",
                                                  "tweet.fields": "created_at,lang,public_metrics",
                                                  "user.fields": "username,description,location,profile_image_url",
                                                  "place.fields": "full_name,country,geo"},
                              results_per_call=500,
                              max_tweets=1000000,
                              endpoint='https://api.twitter.com/2/tweets/search/all',
                              bearer_token=search_args["bearer_token"])
            
            #this gives a list of dictionaries, each containing information on ~500 tweets (which equals the `max_results` variable) - the total sum is the `max_tweets` variable (or less if less tweets are available)
            tweets = [tweet for tweet in list(rs.stream())]
        
            #set all the tweet variables that will be recorded
            author_id_list, created_at_list, lang_list, tweet_id_list, tweet_text_list, likes_list, retweets_list, tweet_place_id_list, bio_location_list, username_list, user_description_list, profile_image_url_list, country_list, place_full_name_list, geo_box_list, place_id_list = ([] for i in range(16))
        
            #extract the information on the tweets
            for t_dict in tweets:
                
                #get the tweet information
                for tweet in t_dict['data']:
                    author_id_list.append(tweet['author_id'])
                    created_at_list.append(tweet['created_at'])
                    lang_list.append(tweet['lang'])
                    tweet_id_list.append(tweet['id']) 
                    tweet_text_list.append(tweet['text'])
                    likes_list.append(tweet['public_metrics']['like_count'])
                    retweets_list.append(tweet['public_metrics']['retweet_count'])
                    
                    try: tweet_place_id_list.append(tweet['geo']['place_id'])
                    except: tweet_place_id_list.append('')
        
                    #get the place information
                    try: country_list.append([x['country'] for x in t_dict['includes']['places'] if x['id'] == tweet['geo']['place_id']][0])
                    except: country_list.append('')
        
                    try: place_full_name_list.append([x['full_name'] for x in t_dict['includes']['places'] if x['id'] == tweet['geo']['place_id']][0])
                    except: place_full_name_list.append('')
        
                    try: geo_box_list.append([x['geo']['bbox'] for x in t_dict['includes']['places'] if x['id'] == tweet['geo']['place_id']][0])
                    except: geo_box_list.append('')
        
                    #get the user information
                    for x in t_dict['includes']['users']:
                        if x['id'] == tweet['author_id']:
                            if 'location' in x:
                                bio_location_list.append(x['location'])
                            else:
                                bio_location_list.append('')
                                
                    username_list.append([x['username'] for x in t_dict['includes']['users'] if x['id'] == tweet['author_id']][0])
                    profile_image_url_list.append([x['profile_image_url'] for x in t_dict['includes']['users'] if x['id'] == tweet['author_id']][0])
                    user_description_list.append([x['description'] for x in t_dict['includes']['users'] if x['id'] == tweet['author_id']][0])
        
            #add all the tweet data to an overall dataset 
            tweet_df = pd.DataFrame({'author_id': author_id_list,
                                     'username': username_list,
                                     'tweet_id': tweet_id_list,
                                     'created_at': created_at_list,
                                     'lang': lang_list,
                                     'tweet_text': tweet_text_list,
                                     'country': country_list,
                                     'place_full_name': place_full_name_list,
                                     'place_geo_box': geo_box_list,
                                     'place_id': tweet_place_id_list,
                                     'likes': likes_list,
                                     'retweets': retweets_list,
                                     'bio_location': bio_location_list,
                                     'profile_image_url': profile_image_url_list,
                                     'user_description': user_description_list})
          
            #add the tweet data to the data for the day
            total_day_dat = total_day_dat.append(tweet_df)
        
        #sort by date and reset index
        total_day_dat['date'] =  pd.to_datetime(total_day_dat['created_at'], format = "%Y-%m-%dT%H:%M:%S.%fZ")
        total_day_dat = total_day_dat.sort_values(by='date',ascending = True)
        total_day_dat = total_day_dat.reset_index(drop=True)
        
        ### ### ###
    
        #create the file name
        lower_country = country.lower()
        filename = '../twitter_data/' + lower_country + '_tweets_' + day.replace('-', '_') + '.csv'
    
        #save the dataframe
        total_day_dat.to_csv(filename, index = False)
        
        #save a pickle of the progress
        dates_saved[country].append(day)    
        
        with open('../progress/dates_saved_eu.pkl', 'wb') as f:
            pickle.dump(dates_saved, f)
            
        #track progress
        print("COUNTRY:", country.upper(), "| SAVED DAY:", day, "| TOTAL TWEETS:", len(total_day_dat), "\n", file = open(progress_output, "a"))
                
