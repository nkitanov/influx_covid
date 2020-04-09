#!/usr/bin/env python3

from influxdb import InfluxDBClient

client = InfluxDBClient(host="192.168.1.201", port=8086, database="home_assistant")
avg = client.query(
    "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' group by time(1d)"
)

# https://influxdb-python.readthedocs.io/en/latest/resultset.html
avg_list = list(avg.get_points())


def rate():
    first = avg_list[-1]["last"]
    second = avg_list[-2]["last"]
    third = avg_list[-3]["last"]
    return round((first - second) / (second - third), 2)


json = [{"fields": {"value": rate()}, "measurement": "covid_confirmed_rate"}]
client.write_points(json)
