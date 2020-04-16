#!/usr/bin/env python3

from influxdb import InfluxDBClient
from datetime import date

today = date.today().isoformat()
client = InfluxDBClient(host="192.168.1.201", port=8086, database="home_assistant")

q = client.query(
    "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed'",
    epoch="s",
)

for i in q.get_points():
    timeh = i["time"]
    half_value = str(i["last"] / 2)

    q = client.query(
        "select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' and value < "
        + half_value
        + "",
        epoch="s",
    )
    lst = list(q.get_points())
    timel = lst[0]["time"]
    days = round((timeh - timel) / 86400, 1)


def db_time2double():
    d = {}
    q = client.query("select last(value) from covid_timedouble")
    lst = list(q.get_points())
    d["days"] = lst[0]["last"]
    d["time"] = lst[0]["time"].split("T")[0]
    return d


if days != db_time2double()["days"]:
    json = [{"fields": {"value": days}, "measurement": "covid_timedouble"}]
    client.write_points(json)
elif today != db_time2double()["time"]:  # Update also if the diff is same for the current day
    json = [{"fields": {"value": days}, "measurement": "covid_timedouble"}]
    client.write_points(json)
