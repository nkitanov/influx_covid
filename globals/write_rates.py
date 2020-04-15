#!/usr/bin/env python3

from influxdb import InfluxDBClient
from country_list import country_list

client = InfluxDBClient(host="192.168.1.201", port=8086, database="covid_global")


def db_daily_rate(country):
    # {'time': '2020-04-14T00:00:00Z', 'rate': None}
    d = {}
    q = client.query(
        "select last(*) from rates where region='"
        + country
        + "' and time = '"
        + daily_rate(country)["time"]
        + "'"
    )
    l = list(q.get_points())
    d["time"] = l[0]["time"]
    d["rate"] = l[0]["last_daily_rate"]
    return d


def db_weekly_rate(country):
    # return last weekly value
    q = client.query(
        "select last(weekly_rate) from rates where region='" + country + "'"
    )
    l = list(q.get_points())
    return l[0]["last"]


def daily_rate(country):
    # {'time': '2020-04-14T00:00:00Z', 'rate': 0.9}
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
    d = {}
    q = client.query(
        "select difference(last(confirmed)) from data where region='"
        + country
        + "' and time > 1579651200 group by time(1w) fill(none)"
    )
    lst = list(q.get_points())
    rate = round(lst[-1]["difference"] / lst[-2]["difference"], 2)
    return float(rate)


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
