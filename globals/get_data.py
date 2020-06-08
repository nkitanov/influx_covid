#!/usr/bin/env python3

import sys
from covid import Covid
from influxdb import InfluxDBClient
from country_list import country_list, continents_dictionary
from datetime import datetime

# Influx host is different if I run it from my Win PC
if sys.platform == "linux":
    influx_host = "localhost"
else:
    influx_host = "35.207.86.81"

client = InfluxDBClient(host=influx_host, port=8086, database="covid_global")
covid = Covid(source="worldometers")

d = {}
global_tests = 0
global_population = 0
utc_hour = int(datetime.utcnow().strftime('%H'))


def db_current(country):
    q = client.query("select last(confirmed) from data where region='" + country + "'")
    lst = list(q.get_points())
    try:
        return lst[-1]["last"]
    except IndexError:
        return 0


if __name__ == "__main__":
    # Calculate Global tests by iterating all countries
    all_countries = covid.list_countries()
    for country in all_countries:
        global_tests += covid.get_status_by_country_name(country)["total_tests"]
        global_population += covid.get_status_by_country_name(country)["population"]

    # Get globals as they cannot be queried by county from covid library
    d["Global"] = {
        "confirmed": covid.get_total_confirmed_cases(),
        "recovered": covid.get_total_recovered(),
        "active": covid.get_total_active_cases(),
        "deaths": covid.get_total_deaths(),
        "total_tests": global_tests,
        "population": global_population,
    }

    # Calculate per continent values as defined in continents_dictionary
    continents = [continent for continent in continents_dictionary]

    for continent in continents:
        country_list_cont = continents_dictionary[continent]
        confirmed = 0
        recovered = 0
        active = 0
        deaths = 0
        tested = 0
        population = 0

        for country in country_list_cont:
            d[country] = covid.get_status_by_country_name(country)
            confirmed += d[country]["confirmed"]
            recovered += d[country]["recovered"]
            active += d[country]["active"]
            deaths += d[country]["deaths"]
            tested += d[country]["total_tests"]
            population += d[country]["population"]

        d[continent] = {}
        d[continent]["confirmed"] = confirmed
        d[continent]["recovered"] = recovered
        d[continent]["active"] = active
        d[continent]["deaths"] = deaths
        d[continent]["total_tests"] = tested
        d[continent]["population"] = population

    for country in country_list:
        if country != "Global":
            # Redefine country for UK and US because wordometers use UK and USA
            # remove the if statement and change wcountry to 'country' argument in covid get statement
            # for John Hopkins data
            if country == "US":
                wcountry = "USA"
            elif country == "United Kingdom":
                wcountry = "UK"
            else:
                wcountry = country
            if country not in continents:
                d[country] = covid.get_status_by_country_name(wcountry)
        json = [
            {
                "measurement": "data",
                "tags": {"region": country},
                "fields": {
                    "confirmed": d[country]["confirmed"],
                    "recovered": d[country]["recovered"],
                    "active": d[country]["active"],
                    "deaths": d[country]["deaths"],
                    "tested": d[country]["total_tests"],
                    "population": int(d[country]["population"]),
                },
            }
        ]

        # Update db only if there is change in confirmed
        if d[country]["confirmed"] != db_current(country):
            # For Bulgaria do not update between 00 and 3AM local as it aggregates for 
            # the previous day (they update at 1-2 AM usually) since influx uses UTC
            if country != "Bulgaria":
                client.write_points(json)
            elif utc_hour < 21:
                client.write_points(json)
