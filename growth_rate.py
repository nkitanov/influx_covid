#!/usr/bin/env python3

from influxdb import InfluxDBClient
from datetime import datetime, timedelta

client = InfluxDBClient(host="192.168.1.201", port=8086, database="home_assistant")

today = (datetime.today() - timedelta(hours=2)).strftime("%Y-%m-%d")


def rate(what):
    daily_last = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' group by time(1d)"
    )
    daily_last_list = []
    # https://influxdb-python.readthedocs.io/en/latest/resultset.html
    for i in daily_last.get_points():
        daily_last_list.append(i)
    first = daily_last_list[-1]["last"]
    second = daily_last_list[-2]["last"]
    third = daily_last_list[-3]["last"]
    if what == "rate":
        if not first:
            first = (
                second  # Redefine variable if today db query is none to use yesterday
            )
        return round((first - second) / (second - third), 2)
    elif what == "today":
        if not first:
            first = 0
        return first


def db_new_daily():
    q = client.query("select last(value) from covid_today_confirmed")
    list = []
    for i in q.get_points():
        list.append(i)
    return list[-1]["last"]


def db_rate():
    q = client.query("select last(value) from covid_current_rate")
    list = []
    for i in q.get_points():
        list.append(i)
    return list[-1]["last"]


def yesterday_cases():
    q = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' and time < '"
        + today
        + "' group by time(1d)"
    )
    list = []
    for i in q.get_points():
        list.append(i)
    if len(list) == 0:
        return 0
    else:
        return list[-1]["last"]


def db_today():
    q = client.query("select last(value) from covid_today_confirmed")
    list = []
    for i in q.get_points():
        list.append(i)
    return list[-1]["last"]


# Update only if there is change
if rate("rate") != db_rate():
    json_rate = [
        {"fields": {"value": rate("rate")}, "measurement": "covid_current_rate"}
    ]
    client.write_points(json_rate)


if rate("today") == 0:
    day_cases = 0
else:
    day_cases = rate("today") - yesterday_cases()

if rate("today") != db_new_daily():
    json_rate = [
        {"fields": {"value": day_cases}, "measurement": "covid_today_confirmed"}
    ]
    client.write_points(json_rate)
