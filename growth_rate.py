#!/usr/bin/env python3

from influxdb import InfluxDBClient

client = InfluxDBClient(host="192.168.1.201", port=8086, database="home_assistant")


def db_rate():
    q = client.query("select last(value) from covid_current_rate")
    lst = list(q.get_points())
    return lst[-1]["last"]


def rate():
    q = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' group by time(1d)"
    )
    lst = list(q.get_points())
    first = lst[-1]["last"]
    second = lst[-2]["last"]
    third = lst[-3]["last"]
    return round((first - second) / (second - third), 2)


def weekly_rate():
    q = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' group by time(1w)"
    )
    lst = list(q.get_points())
    first = lst[-1]["last"]
    second = lst[-2]["last"]
    third = lst[-3]["last"]
    return round((first - second) / (second - third), 2)


def db_weekly_rate():
    q = client.query("select last(value) from covid_weekly_rate")
    lst = list(q.get_points())
    return lst[-1]["last"]


if rate() != db_rate():
    json = [{"fields": {"value": rate()}, "measurement": "covid_current_rate"}]
    client.write_points(json)

if db_weekly_rate() != weekly_rate():
    json = [{"fields": {"value": weekly_rate()}, "measurement": "covid_weekly_rate"}]
    client.write_points(json)
