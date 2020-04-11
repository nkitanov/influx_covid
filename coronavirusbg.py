#!/usr/bin/env python3

from bs4 import BeautifulSoup
from influxdb import InfluxDBClient
import requests

URL = "https://coronavirus.bg/bg/news"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

client = InfluxDBClient(host="192.168.1.201", port=8086, database="home_assistant")


def confirmed():
    return float(soup.find_all("p", "statistics-value")[2].text)


def deaths():
    return float(soup.find_all("p", "statistics-value")[3].text)


def recovered():
    return float(soup.find_all("p", "statistics-value")[4].text)


def tested():
    return float(soup.find_all("p", "statistics-value")[1].text)


def quarantined():
    return float(soup.find_all("p", "statistics-value")[0].text)


def db_deaths():
    q = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_deaths'"
    )
    lst = list(q.get_points())
    return lst[-1]["last"]


def db_confirmed():
    q = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed'"
    )
    lst = list(q.get_points())
    return lst[-1]["last"]


def db_recovered():
    q = client.query("select last(value) from covid_recovered")
    lst = list(q.get_points())
    return lst[-1]["last"]


def db_quarantined():
    q = client.query("select last(value) from covid_quarantined")
    lst = list(q.get_points())
    return lst[-1]["last"]


def db_tested():
    q = client.query("select last(value) from covid_tested")
    lst = list(q.get_points())
    return lst[-1]["last"]


if quarantined() != db_quarantined():
    json = [{"fields": {"value": quarantined()}, "measurement": "covid_quarantined"}]
    client.write_points(json)

if tested() != db_tested():
    json = [{"fields": {"value": tested()}, "measurement": "covid_tested"}]
    client.write_points(json)



# Update db only if there is change
# if mh_confirmed() != db_current_confirmed():
#     json = [
#         {
#             "fields": {
#                 "value": mh_confirmed(),
#                 "attribution_str": "Data by Bulgarian MH",
#             },
#             "measurement": "people",
#             "tags": {"entity_id": "bulgaria_coronavirus_confirmed"},
#         }
#     ]
#     client.write_points(json)

# if mh_deaths() != db_deaths():
#     json = [
#         {
#             "fields": {"value": mh_deaths(), "attribution_str": "Data by Bulgarian MH"},
#             "measurement": "people",
#             "tags": {"entity_id": "bulgaria_coronavirus_deaths"},
#         }
#     ]
#     client.write_points(json)

# if mh_recovered() != db_recovered():
#     json = [{"fields": {"value": mh_recovered()}, "measurement": "covid_recovered"}]
#     client.write_points(json)

# if death_rate() != db_death_rate():
#     json = [{"fields": {"value": death_rate()}, "measurement": "covid_death_rate"}]
#     client.write_points(json)