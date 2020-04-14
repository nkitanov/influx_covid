#!/usr/bin/env python3

from covid import Covid
from influxdb import InfluxDBClient

client = InfluxDBClient(host="192.168.1.201", port=8086, database="covid_global")
covid = Covid()

country_list = [
    "Belgium",
    "Germany",
    "Bulgaria",
    "Japan",
    "China",
    "Malaysia",
    "Ukraine",
    "France",
    "US",
    "Switzerland",
    "United Kingdom",
    "Global"
]

d = {}

# Get globals as they cannot be queried like countres
d["Global"] = {
    "confirmed": covid.get_total_confirmed_cases(),
    "recovered": covid.get_total_recovered(),
    "active": covid.get_total_active_cases(),
    "deaths": covid.get_total_deaths(),
}

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
    client.write_points(json)


