#!/usr/bin/env python3

import sys
from influxdb import InfluxDBClient
from country_list import country_list, population
from get_data import db_current

# Influx host is different if I run it from my Win PC
if sys.platform == "linux":
    influx_host = "localhost"
else:
    influx_host = "35.207.86.81"

client = InfluxDBClient(host=influx_host, port=8086, database="covid_global")


def db_daily_rate(country):
    # Return like {'time': '2020-04-14T00:00:00Z', 'rate': 0.5}
    d = {}
    q = client.query(
        "select last(daily_rate) from rates where region='" + country + "'"
    )
    l = list(q.get_points())
    d["time"] = l[0]["time"]
    d["rate"] = l[0]["last"]
    return d


def db_weekly_rate(country):
    # Return last weekly value
    q = client.query(
        "select last(weekly_rate) from rates where region='" + country + "'"
    )
    l = list(q.get_points())
    return l[0]["last"]


def db_death_rate(country):
    # Return last death rate value
    q = client.query(
        "select last(death_rate) from rates where region = '" + country + "'"
    )
    l = list(q.get_points())
    try:
        return l[0]["last"]
    except IndexError:
        return None


def death_rate(country):
    # Return dict like {'percent': 13.28, 'dpm': 237.09, 'country': 'United Kingdom'}
    d = {}
    q = client.query("select last(*) from data where region = '" + country + "'")
    l = list(q.get_points())
    d["percent"] = round((l[0]["last_deaths"] / l[0]["last_confirmed"]) * 100, 2)
    d["dpm"] = round(l[0]["last_deaths"] / (population[country] / 1e6), 2)
    d["country"] = country
    return d


def db_test_rate(country):
    # Return last test rate per milion value
    q = client.query(
        "select last(tested_milion) from rates where region='" + country + "'",
        epoch="s",
    )
    l = list(q.get_points())
    return l[0]["last"]


def test_rate(country):
    # Return dict like:
    # {'tested_milion': 6694.0, 'tested_confirmed': 30.0, 
    #  'projected_positives': 231615.0, 'projected_positives_percent': 3.33, 
    #  'country': 'Bulgaria'}
    d = {}
    q = client.query("select last(*) from data where region = '" + country + "'")
    l = list(q.get_points())
    d["tested_milion"] = round((l[0]["last_tested"] / (population[country] / 1e6)), 0)
    d["tested_confirmed"] = round(l[0]["last_tested"] / db_current(country), 0)
    if l[0]["last_tested"] > 0:
        d["projected_positives"] = round(population[country] / d["tested_confirmed"], 0)
        d["projected_positives_percent"] = round(
            (d["projected_positives"] / population[country] * 100), 2
        )
    else:
        d["projected_positives"] = 0
        d["projected_positives_percent"] = 0
    d["country"] = country
    return d


def db_timedouble(country):
    # Return last time2double value
    q = client.query(
        "select last(time2double) from rates where region='" + country + "'", epoch="s"
    )
    l = list(q.get_points())
    return l[0]["last"]


def timedouble(country):
    # Return like {'time': 1586936948, 'time2double': 16.3, 'region': 'Bulgaria'}
    d = {}
    q = client.query(
        "select last(confirmed) from data where region='" + country + "'", epoch="s"
    )
    l = list(q.get_points())
    timeh = l[0]["time"]
    half = l[0]["last"] / 2
    q = client.query(
        "select last(confirmed) from data where region='"
        + country
        + "' and confirmed < "
        + str(half)
        + "",
        epoch="s",
    )
    l = list(q.get_points())
    timel = l[0]["time"]
    days = round((timeh - timel) / 86400, 1)
    d["time"] = timeh
    d["time2double"] = days
    d["region"] = country
    return d


def daily_rate(country):
    # Return like {'time': '2020-04-14T00:00:00Z', 'rate': 0.9}
    d = {}
    q = client.query(
        "select difference(last(confirmed)) from data where region='"
        + country
        + "' and time > 1579651200 group by time(1d) fill(none)"
    )
    lst = list(q.get_points())
    d["time"] = lst[-1]["time"]
    try:
        d["rate"] = round(lst[-1]["difference"] / lst[-2]["difference"], 2)
    except ZeroDivisionError:
        d["rate"] = round(
            lst[-1]["difference"], 2
        )  # If no new cases prev day "rate" = new day case
    return d


def weekly_rate(country):
    # return current rate
    q = client.query(
        "select difference(last(confirmed)) from data where region='"
        + country
        + "' and time > 1579651200 group by time(1w) fill(none)"
    )
    lst = list(q.get_points())
    rate = round(lst[-1]["difference"] / lst[-2]["difference"], 2)
    return float(rate)


# Iterate over countries and write db only on change
for country in country_list:
    daily_rate_dict = daily_rate(country)
    if db_daily_rate(country)["rate"] != daily_rate_dict["rate"]:
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "time": daily_rate_dict["time"],
                "fields": {"daily_rate": float(daily_rate_dict["rate"])},
            }
        ]
        client.write_points(json)

    weekly_r = weekly_rate(country)
    if db_weekly_rate(country) != weekly_r:
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "fields": {"weekly_rate": weekly_r},
            }
        ]
        client.write_points(json)

    timedouble_dict = timedouble(country)
    if db_timedouble(country) != timedouble_dict["time2double"]:
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "time": timedouble_dict["time"],
                "fields": {"time2double": timedouble_dict["time2double"]},
            }
        ]
        client.write_points(json, time_precision="s")

    death_rate_dict = death_rate(country)
    if db_death_rate(country) != death_rate_dict["percent"]:
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "fields": {
                    "death_rate": death_rate_dict["percent"],
                    "death_pm": death_rate_dict["dpm"],
                },
            }
        ]
        client.write_points(json)

    test_rate_dict = test_rate(country)
    if db_test_rate(country) != test_rate_dict["tested_milion"]:
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "fields": {
                    "tested_milion": test_rate_dict["tested_milion"],
                    "tested_confirmed": test_rate_dict["tested_confirmed"],
                    "projected_positives": float(test_rate_dict["projected_positives"]),
                    "projected_positives_percent": float(test_rate_dict["projected_positives_percent"])
                },
            }
        ]
        client.write_points(json)
