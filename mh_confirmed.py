#!/usr/bin/env python3

from bs4 import BeautifulSoup
from influxdb import InfluxDBClient
import requests

URL = "https://www.mh.government.bg/bg/informaciya-za-grazhdani/potvrdeni-sluchai-na-koronavirus-na-teritoriyata-na-r-blgariya/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

client = InfluxDBClient(host="192.168.1.201", port=8086, database="home_assistant")


def mh_confirmed():
    return float(soup.find_all("td")[1].text)


def mh_deaths():
    return float(soup.find_all("td")[3].text)


def mh_recovered():
    return float(soup.find_all("td")[5].text)


def death_rate():
    return round(mh_deaths() / mh_confirmed() * 100, 2)


def db_deaths():
    q = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_deaths'"
    )
    list = []
    for i in q.get_points():
        list.append(i)
    return list[-1]["last"]


def db_current_confirmed():
    q = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed'"
    )
    list = []
    for i in q.get_points():
        list.append(i)
    return list[-1]["last"]


def db_recovered():
    q = client.query("select last(value) from covid_recovered")
    list = []
    for i in q.get_points():
        list.append(i)
    return list[-1]["last"]


def db_death_rate():
    q = client.query("select last(value) from covid_death_rate")
    list = []
    for i in q.get_points():
        list.append(i)
    return list[-1]["last"]


def weekly_cases():
    q = client.query(
        "SELECT last(value) FROM people WHERE entity_id = 'bulgaria_coronavirus_confirmed' GROUP BY time(1w)"
    )
    list = []
    for i in q.get_points():
        list.append(i)
    return float(list[-1]["last"] - list[-2]["last"])


def db_weekly_cases():
    q = client.query("select last(value) from covid_weekly")
    list = []
    for i in q.get_points():
        list.append(i)
    return list[-1]["last"]


def weekly_rate():
    q = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' group by time(1w)"
    )
    list = []
    for i in q.get_points():
        list.append(i)
    first = list[-1]["last"]
    second = list[-2]["last"]
    third = list[-3]["last"]
    return round((first - second) / (second - third), 2)


def db_weekly_rate():
    q = client.query("select last(value) from covid_weekly_rate")
    list = []
    for i in q.get_points():
        list.append(i)
    return list[-1]["last"]


# Update db only if there is change
if mh_confirmed() != db_current_confirmed():
    json = [
        {
            "fields": {
                "value": mh_confirmed(),
                "attribution_str": "Data by Bulgarian MH",
            },
            "measurement": "people",
            "tags": {"entity_id": "bulgaria_coronavirus_confirmed"},
        }
    ]
    client.write_points(json)

if mh_deaths() != db_deaths():
    json = [
        {
            "fields": {"value": mh_deaths(), "attribution_str": "Data by Bulgarian MH"},
            "measurement": "people",
            "tags": {"entity_id": "bulgaria_coronavirus_deaths"},
        }
    ]
    client.write_points(json)

if mh_recovered() != db_recovered():
    json = [{"fields": {"value": mh_recovered()}, "measurement": "covid_recovered"}]
    client.write_points(json)

if death_rate() != db_death_rate():
    json = [{"fields": {"value": death_rate()}, "measurement": "covid_death_rate"}]
    client.write_points(json)

if db_weekly_cases() != weekly_cases():
    json = [{"fields": {"value": weekly_cases()}, "measurement": "covid_weekly"}]
    client.write_points(json)

if db_weekly_rate() != weekly_rate():
    json = [{"fields": {"value": weekly_rate()}, "measurement": "covid_weekly_rate"}]
    client.write_points(json)
