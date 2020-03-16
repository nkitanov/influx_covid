#!/usr/bin/env python3

from influxdb import InfluxDBClient

client = InfluxDBClient(host="192.168.1.201", port=8086, database="home_assistant")
avg = client.query(
    "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' group by time(1d)"
)
avg_list = []

# https://influxdb-python.readthedocs.io/en/latest/resultset.html
for i in avg.get_points():
    avg_list.append(i)


def diff():
    fin = avg_list[-1]["last"]
    prev = avg_list[-2]["last"]
    return float(fin - prev)


def rate():
    first = avg_list[-1]["last"]
    second = avg_list[-2]["last"]
    third = avg_list[-3]["last"]
    return round((first - second) / (second - third), 2)


json_diff = [{"fields": {"value": diff()}, "measurement": "covid_confirmed_diff"}]
json_rate = [{"fields": {"value": rate()}, "measurement": "covid_confirmed_rate"}]
client.write_points(json_diff)
client.write_points(json_rate)
