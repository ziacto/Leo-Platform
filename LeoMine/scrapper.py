import pandas as pd
import pymongo
from newspaper import Article
import json
from datetime import datetime
import re
import requests
from crimewise import CrimewiseScrapper
import os

from sources.deccan_chronicle import DeccanChronicleScrapper
from sources.hindustan_times import HindustanTimesScrapper
from sources.ndtv import NdtvScrapper
from sources.the_hindu import TheHinduScrapper
from sources.toi import ToiScrapper
from sources.tweets_scrapper import TweetsScrapper
from utils.modules import *

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')

def MakeConnections()  :
    '''
        Make Database connection
    '''
    client = pymongo.MongoClient(
        "mongodb+srv://praj:pra@cluster0-jpt7l.mongodb.net/test?retryWrites=true&w=majority"
    )
    db = client.get_database("Leo")

    # Drop existing collections
    """ db.news.drop()
    db.crimes.drop() """

    # Create index on city in news collection
    db.news.create_index(
        [("city", pymongo.TEXT)], name="search_index", default_language="english"
    )

    # Create index on loc in crimes collection
    db.crimes.create_index([("loc", pymongo.GEOSPHERE)], name="geosearch_index")

    return db

def DumpIntoDb(db, json_news) :
    '''
        Dump the data scrapped and processed into database
    '''
    result = db.news.insert_many(json_news)
    print("Number of news saved into database:", len(result.inserted_ids))

    with open("./database/data.json") as handle:
        # Load data from JSON to dict
        file_data = json.load(handle)
        # Iterate over list of crime objects
        results = []
        for data in file_data:
            # Fetch approximate coordinates of region
            location_details = requests.get(
                "https://api.opencagedata.com/geocode/v1/json?q="
                + data["Regions"].strip()
                + "&key="+API_KEY
            ).json()

            # Try removing white spaces and retry
            if len(location_details["results"]) == 0:
                location_details = requests.get(
                    "https://api.opencagedata.com/geocode/v1/json?q="
                    + data["Regions"].replace(" ", "")
                    + "&key="+API_KEY
                ).json()
                if len(location_details["results"]) == 0:
                    latitude, longitude = 0.0, 0.0
                else:
                    latitude, longitude = location_details["results"][0][
                        "geometry"
                    ].values()
            else:
                latitude, longitude = location_details["results"][0][
                    "geometry"
                ].values()

            # Make an UPSERT query
            result = db.crimes.update_one(
                {"region": data["Regions"]},
                {
                    "$set": {
                        "region": data["Regions"],
                        "city": data["City"],
                        "loc": {"type": "Point", "coordinates": [longitude, latitude],},
                        "murder": data["Murder"],
                        "rape": data["Rape"],
                        "kidnapping": data["Kidnapping"],
                        "robbery": data["Robbery"],
                        "holding hostage": data["Holding hostage"],
                        "riot": data["Riot"],
                        "arson": data["Arson"],
                        "assault": data["Assault"],
                        "covid": data["Covid"],
                    }
                },
                upsert=True,
            )
            results.append(result.upserted_id)
            #print("bhnm")
        print("Number of crimes upserted into database:", len(results))

    print("done")


def LeoMineScraper(db):
    '''
        Scrap news articles from various sources and check for duplicates
    '''
    retVal = DeccanChronicleScrapper()
    if not (retVal.empty):
        df = retVal
    retVal = NdtvScrapper()
    if not (retVal.empty):
        if not df.empty:
            df = df.append(retVal, ignore_index=True)
        else:
            df = df.append(retVal)
    print(df.shape)
    retVal = HindustanTimesScrapper()
    if not (retVal.empty):
        if not df.empty:
            df = df.append(retVal, ignore_index=True)
        else:
            df = df.append(retVal)
    print(df.shape)

    retVal = TheHinduScrapper()
    if not (retVal.empty):
        if not df.empty:
            df = df.append(retVal, ignore_index=True)
        else:
            df = df.append(retVal)
    print(df.shape)

    retVal = TweetsScrapper()
    if not (retVal.empty):
        if not df.empty:
            df = df.append(retVal, ignore_index=True)
        else:
            df = df.append(retVal)
    print(df.shape)
            
    retVal = ToiScrapper()
    if not(retVal.empty) :
        if not df.empty:
            df = df.append(retVal, ignore_index=True)
        else :
            df = df.append(retVal)
    print(df.shape)

    
    client = pymongo.MongoClient(
        "mongodb+srv://praj:pra@cluster0-jpt7l.mongodb.net/test?retryWrites=true&w=majority"
    )
    db = client.get_database("Leo")
    final_df = pd.DataFrame(columns=df.columns)

    for index, row in df.iterrows():
        query = {"url": row["url"]}
        cursor = db.news.find(query)
        lst = list(cursor)
        if len(lst) == 0:
            query = {
                "date": row["date"],
                "crime": row["crime"],
                "region": re.compile(row["region"], re.IGNORECASE),
                "city": re.compile(row["city"], re.IGNORECASE),
            }
            cursor = db.news.find(query)
            lst = list(cursor)
            if len(lst) == 0:
                final_df = final_df.append(row, ignore_index=True)
    saving_articles(final_df, "./database/headlines.csv")
    data = get_data("./database/data.json")
    data_ = preprocessing(final_df, data)
    save_data(data_, "./database/data.json")
    
    print(final_df.shape)
    return final_df
    
def DumpingStats(db) :
    with open("./database/data.json") as handle:
        # Load data from JSON to dict
        file_data = json.load(handle)
        # Iterate over list of crime objects
        results = []
        for data in file_data:
            # Fetch approximate coordinates of region
            location_details = requests.get(
                "https://api.opencagedata.com/geocode/v1/json?q="
                + data["Regions"].strip()
                + "&key="+API_KEY
            ).json()

            # Try removing white spaces and retry
            if len(location_details["results"]) == 0:
                location_details = requests.get(
                    "https://api.opencagedata.com/geocode/v1/json?q="
                    + data["Regions"].replace(" ", "")
                    + "&key="+API_KEY
                ).json()
                if len(location_details["results"]) == 0:
                    latitude, longitude = 0.0, 0.0
                else:
                    latitude, longitude = location_details["results"][0][
                        "geometry"
                    ].values()
            else:
                latitude, longitude = location_details["results"][0][
                    "geometry"
                ].values()

            # Make an UPSERT query
            result = db.crimes.update_one(
                {"region": data["Regions"]},
                {
                    "$set": {
                        "region": data["Regions"],
                        "city": data["City"],
                        "loc": {
                            "type": "Point",
                            "coordinates": [longitude, latitude],
                        },
                        "murder": data["Murder"],
                        "rape": data["Rape"],
                        "kidnapping": data["Kidnapping"],
                        "robbery": data["Robbery"],
                        "holding hostage": data["Holding hostage"],
                        "riot": data["Riot"],
                        "arson": data["Arson"],
                        "assault": data["Assault"],
                        "covid": data["Covid"],
                    }
                },
                upsert=True,
            )
            results.append(result.upserted_id)
            #print("bhnm")
        print("Number of crimes upserted into database:", len(results))
            
        print("done")
        
def LoadingPublicDataOneTime(db) :
    excel_file = "./database/public_data.xlsx"
    df = pd.read_excel(excel_file)
    #print(df.columns)
    with open("./database/data.json", encoding='utf-8', errors='ignore') as json_data:
        org_data = json.load(json_data, strict=False)
    #final_df = pd.DataFrame(data.columns)
    results = []
    for _, row in df.iterrows() :
        NewRow = {
            "Regions": row["District/ Area"], 
            "City": row["city"], 
            "Latitude": "", 
            "Longitude": "", 
            "Murder": 0, 
            "Rape": row["Rape"], 
            "Kidnapping": row["Kidnapping"], 
            "Robbery": 0, 
            "Holding hostage": 0, 
            "Riot": 0, 
            "Arson": 0, 
            "Assault": row["Assault"], 
            "Covid": 0
        }
        results.append(NewRow)
        org_data.append(NewRow)
    
    for data in results :
        try :
            location_details = requests.get(
                "https://api.opencagedata.com/geocode/v1/json?q="
                + data["Regions"].strip()
                + "&key="+API_KEY
            ).json()

            # Try removing white spaces and retry
            if len(location_details["results"]) == 0:
                location_details = requests.get(
                    "https://api.opencagedata.com/geocode/v1/json?q="
                    + data["Regions"].replace(" ", "")
                    + "&key="+API_KEY
                ).json()
                if len(location_details["results"]) == 0:
                    latitude, longitude = 0.0, 0.0
                else:
                    latitude, longitude = location_details["results"][0][
                        "geometry"
                    ].values()
            else:
                latitude, longitude = location_details["results"][0][
                    "geometry"
                ].values()


            result = db.crimes.update_one(
                    {"region": data["Regions"]},
                    {
                        "$set": {
                            "region": data["Regions"],
                            "city": data["City"],
                            "loc": {"type": "Point", "coordinates": [longitude, latitude],},
                            "murder": data["Murder"],
                            "rape": data["Rape"],
                            "kidnapping": data["Kidnapping"],
                            "robbery": data["Robbery"],
                            "holding hostage": data["Holding hostage"],
                            "riot": data["Riot"],
                            "arson": data["Arson"],
                            "assault": data["Assault"],
                            "covid": data["Covid"],
                        }
                    },
                    upsert=True,
                )
            results.append(result.upserted_id)
            print("ok")
            
        except :
            print("fail")
    print("Number of crimes upserted into database:", len(results))
    with open('./database/data.json', 'w') as f:
        json.dump(org_data, f)
#print(data.columns)
        
        
if __name__ == "__main__":
    print("start")
    db = MakeConnections()
    print("setup done")
    print("scrapping...")
    final_df = LeoMineScraper(db)
    #final_df = CrimewiseScrapper()
    print(final_df["headline"])
    if(final_df.empty) :
        print("exit")
    else :
        json_news = final_df.to_dict(orient="records")
        print("dumping into db")
        DumpIntoDb(db, json_news)
        print("exit")
    '''db = MakeConnections()
    LoadingPublicDataOneTime(db)'''
