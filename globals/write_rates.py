#!/usr/bin/env python3

from influxdb import InfluxDBClient
from country_list import country_list, population

client = InfluxDBClient(host="192.168.1.201", port=8086, database="covid_global")


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
    d["rate"] = round(lst[-1]["difference"] / lst[-2]["difference"], 2)
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

    if db_daily_rate(country)["rate"] != daily_rate(country)["rate"]:
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "time": daily_rate(country)["time"],
                "fields": {"daily_rate": daily_rate(country)["rate"]},
            }
        ]
        client.write_points(json)

    if db_weekly_rate(country) != weekly_rate(country):
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "fields": {"weekly_rate": weekly_rate(country)},
            }
        ]
        client.write_points(json)

    if db_timedouble(country) != timedouble(country):
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "time": timedouble(country)["time"],
                "fields": {"time2double": timedouble(country)["time2double"]},
            }
        ]
        client.write_points(json, time_precision="s")

    if db_death_rate(country) != death_rate(country)["percent"]:
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "fields": {
                    "death_rate": death_rate(country)["percent"],
                    "death_pm": death_rate(country)["dpm"],
                },
            }
        ]
        client.write_points(json)
