#!/usr/bin/env python3

from influxdb import InfluxDBClient

client = InfluxDBClient(host="35.207.86.81", port=8086, database="covid_global")

# Control manually list of countries to import (don't import from country_list)
country_list = ["Europe", "North America", "South America", "Asia", "Africa"]


def db_current_daily(country):
    q = client.query(
        "select difference(last(confirmed)) from data where region='"
        + country
        + "' and time > 1579651200 group by time(1d)"
    )
    lst = list(q.get_points())
    return lst


def db_current_weekly(country):
    q = client.query(
        "select difference(last(confirmed)) from data where region='"
        + country
        + "' and time > 1579651200 group by time(1w)"
    )
    lst = list(q.get_points())
    return lst


def rate(country, mode):

    # return list of confirmed rates in dict like
    # 1d: {'time': '2020-03-25T00:00:00Z', 'daily_rate': 1.5, 'region': 'US'}
    # 1w: {'time': '2020-02-06T00:00:00Z', 'weekly_rate': 0.43, 'region': 'US'}

    if mode == "1d":
        lst = db_current_daily(country)
    elif mode == "1w":
        lst = db_current_weekly(country)

    l = []

    for x in range(1, len(lst) - 1):
        d = {}
        try:
            r = round(lst[x]["difference"] / lst[x - 1]["difference"], 2)
        except ZeroDivisionError:
            r = lst[x]["difference"]
        d["time"] = lst[x]["time"]
        if mode == "1d":
            d["daily_rate"] = float(r)
        else:
            d["weekly_rate"] = float(r)
        d["region"] = country
        l.append(d)
    return l


def time2double(country):

    # returns list of dict like
    # [{'time': 1579910400, 'time2double': 0.1}, {'time': 1579996800, 'time2double': 1.1}]

    # Build list with all days
    q = client.query(
        "select last(confirmed) from data where region='"
        + country
        + "' group by time(1d)",
        epoch="s",
    )
    result = list(q.get_points())
    l = []
    for x in range(len(result)):
        d = {}
        try:
            half = float(result[x]["last"] / 2)
        except TypeError:
            continue
        dateh = result[x]["time"]
        q = client.query(
            "select last(confirmed) from data where region='"
            + country
            + "' and confirmed < "
            + str(half)
            + "",
            epoch="s",
        )
        lst = list(q.get_points())
        try:
            datel = lst[0]["time"]
        except IndexError:
            continue
        days = round((dateh - datel) / 86400, 1)
        d["time"] = dateh
        d["time2double"] = float(days)
        l.append(d)
    return l


for country in country_list:

    lst = time2double(country)
    for x in lst:
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "time": x["time"],
                "fields": {"time2double": x["time2double"]},
            }
        ]
        client.write_points(json, time_precision="s")

    lst = rate(country, "1w")
    for x in lst:
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "time": x["time"],
                "fields": {"weekly_rate": x["weekly_rate"]},
            }
        ]
        client.write_points(json)

    lst = rate(country, "1d")
    for x in lst:
        json = [
            {
                "measurement": "rates",
                "tags": {"region": country},
                "time": x["time"],
                "fields": {"daily_rate": x["daily_rate"]},
            }
        ]
        client.write_points(json)
