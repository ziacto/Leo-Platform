"""
This module scrapes content from Deccan Chronicle News.

It provides:
- get_chronological_headlines(url)
- get_trending_headlines(url)
"""

import json
import warnings

from utils.modules import (check_for_duplicates, check_url_in_database,
                           get_data, get_date, preprocessing, preprocessing2,
                           save_data, saving_articles)
from utils.utils import get_crime, get_location

warnings.filterwarnings(action="ignore")
import os
from sys import path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from newspaper import Article

path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from sources.newscrape_common import (is_string, ist_to_utc,
                                      remove_duplicate_entries, str_is_set)
from sources.sources import KNOWN_NEWS_SOURCES


def get_all_content(objects):
    """
    Call this function with a list of objects. Make sure there are no duplicate
    copies of an object else downloading might take long time.
    """

    def get_content(url):
        response = requests.get(url)
        if response.status_code == 200:
            html_content = BeautifulSoup(response.text, "html.parser")
            # a bit erraneous
            # contents sometimes include unwanted text when they too are defined in p tag
            contents = html_content.find("div", {"id": "storyBody"}).find_all(
                lambda tag: tag.name == "p" and not tag.img, recursive=False
            )
            text = ""
            for cont in contents:
                text += cont.get_text() + "\n"
            return text
        return "NA"

    for obj in objects:
        obj["content"] = get_content(obj["link"])


def get_headline_details(obj):
    try:
        from datetime import datetime

        timestamp_tag = obj.find("span", {"class": "SunChDt2"})
        if timestamp_tag is None:
            timestamp = datetime.now()
        else:
            content = timestamp_tag.contents[0].strip()
            timestamp = datetime.strptime(content, "%d %b %Y %I:%M %p")
        return {
            "content": "NA",
            "link": "https://www.deccanchronicle.com" + obj["href"],
            "scraped_at": datetime.utcnow().isoformat(),
            "published_at": ist_to_utc(timestamp).isoformat(),
            "title": obj.find(["h3", "h2"]).contents[0].strip(),
        }
    except KeyError:
        import pdb

        pdb.set_trace()


def get_chronological_headlines(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        a_tags = list(
            map(
                lambda x: x.find("div", {"class": "col-sm-8"}).find("a"),
                soup.find_all("div", {"class": "col-sm-12 SunChNewListing"}),
            )
        )
        headlines = list(map(get_headline_details, a_tags))
        get_all_content(headlines)  # Fetch contents separately
        return headlines
    return None


def get_trending_headlines(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        a_tags = (
            list(
                soup.find("div", {"class": "col-sm-7 noPadding"}).find_all(
                    "a", {"class": "col-sm-12 noPadding"}
                )
            )
            + list(soup.find("div", {"class": "col-sm-5 tsSmall"}).find_all("a"))[:-1]
        )
        headlines = list(map(get_headline_details, a_tags))
        return headlines
    return None


def DeccanChronicleScrapper():

    SRC = KNOWN_NEWS_SOURCES["Deccan Chronicle"]
    data1 = get_chronological_headlines(SRC["pages"].format(1))
    data2 = get_trending_headlines(SRC["home"])
    text_lst = []
    url_lst = []
    date_lst = []
    title_lst = []
    try :
        for data in data1:
            if data["content"] == "NA":
                try:
                    article = Article(data["link"])
                    article.download()
                    article.parse()
                    article.nlp()
                    summary = article.text
                    text_lst.append(summary)
                except:
                    text_lst.append(data["content"])
            else:
                text_lst.append(data["content"])
            url_lst.append(data["link"])
            date = data["published_at"]
            if(date == None) :
                date = datetime.now()
            date_lst.append(date)
            try :
                title_lst.append(data["title"])
            except:
                title_lst.append(data["content"].replace("\n\n", " ").replace("\n", " ").split(".")[0])
        for data in data2:
            if data["content"] == "NA":
                try:
                    article = Article(data["link"])
                    article.download()
                    article.parse()
                    article.nlp()
                    summary = article.text
                    text_lst.append(summary)
                except:
                    text_lst.append(data["content"])
            else:
                text_lst.append(data["content"])
            url_lst.append(data["link"])
            date = data["published_at"]
            if(date == None) :
                date = datetime.now()
            date_lst.append(date)
            try :
                title_lst.append(data["title"])
            except:
                title_lst.append(data["content"].replace("\n\n", " ").replace("\n", " ").split(".")[0])

        df_raw = pd.DataFrame(list(zip(text_lst, url_lst, date_lst, title_lst)), columns=["text", "url", "date", "headline"])

        df_crime = get_crime(df_raw)
        data = get_data("./database/data.json")
        df = get_location(df_crime, data)
        df = preprocessing2(df, data)
        return df.reset_index(drop=True)
    except :
        return pd.DataFrame(columns=["index","text","url","crime","location","region","city","date","headline"])

    # DeccanChronicleScrapper()
