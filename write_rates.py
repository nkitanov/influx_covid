#!/usr/bin/env python3

from country_list import country_list
from influx_connection import client


def db_daily_rate(country):
    # Return like {'time': '2020-04-14T00:00:00Z', 'rate': 0.5}
    d = {}
    q = client.query(
        "select last(daily_rate) from rates where region='" + country + "'"
    )
    l = list(q.get_points())
    if len(l) > 1:
        d["time"] = l[0]["time"]
        d["rate"] = l[0]["last"]
    else:
        d["time"] = 0
        d["rate"] = 0
    return d


def db_weekly_rate(country):
    # Return last weekly value
    q = client.query(
        "select last(weekly_rate) from rates where region='" + country + "'"
    )
    l = list(q.get_points())
    if len(l) >= 1:
        return l[0]["last"]
    else:
        return 0


def db_timedouble(country):
    # Return last time2double value
    q = client.query(
        "select last(time2double) from rates where region='" + country + "'", epoch="s"
    )
    l = list(q.get_points())
    if len(l) > 1:
        return l[0]["last"]
    else:
        return 0


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
    try:
        timel = l[0]["time"]
        days = round((timeh - timel) / 86400, 1)
    except IndexError:
        days = -1.0
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
    try:
        d["time"] = lst[-1]["time"]
    except IndexError:
        d["time"] = 0
    try:
        d["rate"] = round(lst[-1]["difference"] / lst[-2]["difference"], 2)
    except ZeroDivisionError:
        d["rate"] = round(
            lst[-1]["difference"], 2
        )  # If no new cases prev day "rate" = new day case
    except IndexError:
        d["rate"] = 0
    # Growth rate cannot be negative, if there is a daily negative correction keep growth rate at 0
    if d["rate"] < 0:
        d["rate"] = 0
    return d


def weekly_rate(country):
    # return current rate
    q = client.query(
        "select difference(last(confirmed)) from data where region='"
        + country
        + "' and time > 1579651200 group by time(1w, 4d) fill(none)"
    )
    lst = list(q.get_points())
    try:
        rate = round(lst[-1]["difference"] / lst[-2]["difference"], 2)
    except IndexError:
        rate = 0
    return float(rate)


# Iterate over countries and write db only on change
for country in country_list:
    daily_rate_dict = daily_rate(country)
    db_daily_rate_dict = db_daily_rate(country)
    if (
        db_daily_rate_dict["rate"] != daily_rate_dict["rate"]
        or db_daily_rate_dict["time"] != daily_rate_dict["time"]
    ):
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
