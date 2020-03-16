#!/usr/bin/env python3

from influxdb import InfluxDBClient

client = InfluxDBClient(host="192.168.1.201", port=8086, database="home_assistant")


def rate():
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
    return round((first - second) / (second - third), 2)


def db_rate():
    ratedb = client.query(" select last(value) from covid_current_rate")
    ratedb_list = []
    for i in ratedb.get_points():
        ratedb_list.append(i)
    return ratedb_list[-1]["last"]


if rate() != db_rate():
    json_rate = [{"fields": {"value": rate()}, "measurement": "covid_current_rate"}]
    client.write_points(json_rate)