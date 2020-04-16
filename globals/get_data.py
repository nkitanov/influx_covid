#!/usr/bin/env python3

from covid import Covid
from influxdb import InfluxDBClient
from country_list import country_list

client = InfluxDBClient(host="192.168.1.201", port=8086, database="covid_global")
covid = Covid()

d = {}

# Get globals as they cannot be queried by county from covid library
d["Global"] = {
    "confirmed": covid.get_total_confirmed_cases(),
    "recovered": covid.get_total_recovered(),
    "active": covid.get_total_active_cases(),
    "deaths": covid.get_total_deaths(),
}


def db_current(country):
    q = client.query("select last(confirmed) from data where region='" + country + "'")
    lst = list(q.get_points())
    return lst[-1]["last"]


for country in country_list:
    if country != "Global":
        d[country] = covid.get_status_by_country_name(country)
    json = [
        {
            "measurement": "data",
            "tags": {"region": country},
            "fields": {
                "confirmed": d[country]["confirmed"],
                "recovered": d[country]["recovered"],
                "active": d[country]["active"],
                "deaths": d[country]["deaths"],
            },
        }
    ]
    # Update db only if there is change in confirmed
    if d[country]["confirmed"] != db_current(country):
        client.write_points(json)
