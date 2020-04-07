#!/usr/bin/env python3

from influxdb import InfluxDBClient
from datetime import date

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


def timedouble():
    q = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed'"
    )
    list = []
    for i in q.get_points():
        list.append(i)
    dateh = list[0]["time"].split("T")[0].split("-")
    yearh = int(dateh[0])
    monthh = int(dateh[1])
    dayh = int(dateh[2])
    half_value = str(list[0]["last"] / 2)

    q = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' and value < "
        + half_value
        + ""
    )
    list = []
    for i in q.get_points():
        list.append(i)
    datel = list[0]["time"].split("T")[0].split("-")
    yearl = int(datel[0])
    monthl = int(datel[1])
    dayl = int(datel[2])

    diff = (date(yearh, monthh, dayh) - date(yearl, monthl, dayl)).days
    date_db = str(yearh) + "-" + str(monthh) + "-" + str(dayh)
    return [date_db, diff]


json_diff = [{"fields": {"value": diff()}, "measurement": "covid_confirmed_diff"}]
json_rate = [{"fields": {"value": rate()}, "measurement": "covid_confirmed_rate"}]
json_timedouble = [
    {"fields": {"value": timedouble()[1]}, "measurement": "covid_timedouble"}
]
client.write_points(json_timedouble)
client.write_points(json_diff)
client.write_points(json_rate)