#!/usr/bin/env python3
from bs4 import BeautifulSoup
from influxdb import InfluxDBClient
from datetime import datetime
import requests
import sys


URL = "https://coronavirus.bg/bg/news"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
utc_hour = int(datetime.utcnow().strftime("%H"))

# Influx host is different if I run it from my Win PC
if sys.platform == "linux":
    influx_host = "localhost"
else:
    influx_host = "35.207.86.81"

client = InfluxDBClient(host=influx_host, port=8086, database="covid_global")
stats = soup.find(
    "div", attrs={"class": "row statistics-container inner-page-statistics"}
)


def pull_stats(what):
    if what == "hospitalized":
        return int(stats.find_all("p")[12].text)
    elif what == "in_icu":
        return int(stats.find_all("p")[14].text)


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


def rate(what):
    if what == "hospitalization":
        return float(round(pull_stats("hospitalized") / db_stats("active"), 2))
    if what == "icu":
        return float(round(pull_stats("in_icu") / db_stats("hospitalized"), 2))


if pull_stats("hospitalized") != db_stats("hospitalized") or pull_stats(
    "in_icu"
) != db_stats("in_icu"):
    json_data = [
        {
            "measurement": "data",
            "tags": {"region": "Bulgaria"},
            "fields": {
                "hospitalized": pull_stats("hospitalized"),
                "in_icu": pull_stats("in_icu"),
            },
        }
    ]
    json_rates = [
        {
            "measurement": "rates",
            "tags": {"region": "Bulgaria"},
            "fields": {
                "hospitalization_rate": rate("hospitalization"),
                "icu_rate": rate("icu"),
            },
        }
    ]
    if utc_hour < 21:
        client.write_points(json_data)
        client.write_points(json_rates)
