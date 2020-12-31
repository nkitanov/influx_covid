#!/usr/bin/env python3
from bs4 import BeautifulSoup
from influxdb import InfluxDBClient
from datetime import datetime
from influx_connection import client
import requests
import sys


URL = "https://coronavirus.bg/bg/news"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
utc_hour = int(datetime.utcnow().strftime("%H"))

stats = soup.find(
    "div", attrs={"class": "row statistics-container inner-page-statistics"}
)


def pull_stats(what):
    if what == "hospitalized":
        return int(stats.find_all("p")[12].text)
    elif what == "in_icu":
        return int(stats.find_all("p")[14].text)
    elif what == "vaccinated":
        return int(stats.find_all("p")[20].text)


def db_stats(what):
    # return dict
    q = client.query("select last(*) from data where region='Bulgaria'")
    lst = list(q.get_points())
    if what == "hospitalized":
        return int(lst[0]["last_hospitalized"])
    elif what == "in_icu":
        return int(lst[0]["last_in_icu"])
    elif what == "active":
        return int(lst[0]["last_active"])
    elif what == "vaccinated":
        return int(lst[0]["last_vaccinated"])


if (
    pull_stats("hospitalized") != db_stats("hospitalized")
    or pull_stats("in_icu") != db_stats("in_icu")
    or pull_stats("vaccinated") != db_stats("vaccinated")
):
    json_data = [
        {
            "measurement": "data",
            "tags": {"region": "Bulgaria"},
            "fields": {
                "hospitalized": pull_stats("hospitalized"),
                "in_icu": pull_stats("in_icu"),
                "vaccinated": rate("vaccinated"),
            },
        }
    ]

    if utc_hour < 21:
        client.write_points(json_data)