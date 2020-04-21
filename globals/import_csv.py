# Script to parse csv files from https://github.com/CSSEGISandData/COVID-19
# and push the data to Influxdb
# Edit variables for your env

import csv
import os
from datetime import datetime
from influxdb import InfluxDBClient

client = InfluxDBClient(host="192.168.1.201", port=8086, database="covid_global")

# Path to csv files
path = "C:/Users/nki/git/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"

# Control manually list of countries to import (don't import from country_list)
country_list = ["Turkey", "Greece", "Serbia", "Romania"]


def date_convert(csv_date):
    epoch_date = int(
        datetime.strptime(csv_date, "%m-%d-%Y").timestamp() + 10800
    )  # Shift time forward to be 00:00 GMT
    return epoch_date


# Function return dictionary like, time in UNIX seconds based on file name date
# {'confirmed': 15348, 'recovered': 2495, 'deaths': 1011, 'active': 14337, 'time': 1585774800, 'region': 'Belgium'}
def get_numbers(csv_loc):

    d = {}
    confirmed = 0
    active = 0
    deaths = 0
    recovered = 0

    with open(csv_loc, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["Confirmed"]:
                confirmed += int(row["Confirmed"])
            else:
                confirmed += 0
            if row["Recovered"]:
                recovered += int(row["Recovered"])
            else:
                recovered += 0
            if row["Deaths"]:
                deaths += int(row["Deaths"])
            else:
                deaths += 0
        active = confirmed - deaths - recovered
        d["confirmed"] = confirmed
        d["recovered"] = recovered
        d["deaths"] = deaths
        d["active"] = active
        d["time"] = date_convert(csv_date)
    return d


def get_numbers_country(csv_loc, country):

    d = {}
    confirmed = 0
    active = 0
    deaths = 0
    recovered = 0

    with open(csv_loc, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        # Change in column name
        if date_convert(csv_date) < 1584828000:
            cformat = "Country/Region"
        else:
            cformat = "Country_Region"

        for row in reader:
            if (row["Confirmed"]) and (row[cformat] == country):
                confirmed += int(row["Confirmed"])
            else:
                confirmed += 0
            if (row["Recovered"]) and (row[cformat] == country):
                recovered += int(row["Recovered"])
            else:
                recovered += 0
            if (row["Deaths"]) and (row[cformat] == country):
                deaths += int(row["Deaths"])
            else:
                recovered += 0
        active = confirmed - deaths - recovered
        d["confirmed"] = confirmed
        d["recovered"] = recovered
        d["deaths"] = deaths
        d["active"] = active
        d["time"] = date_convert(csv_date)
        d["region"] = country
    return d


for country in country_list:
    dir_list = os.scandir(path)
    for f in dir_list:
        csv_loc = path + f.name
        csv_date = (os.path.splitext(csv_loc)[0]).split("/")[-1]
        if country == "Global":
            d = get_numbers(csv_loc)
        else:
            d = get_numbers_country(csv_loc, country)

        json = [
            {
                "measurement": "data",
                "tags": {"region": country},
                "time": d["time"],
                "fields": {
                    "confirmed": d["confirmed"],
                    "recovered": d["recovered"],
                    "active": d["active"],
                    "deaths": d["deaths"],
                },
            }
        ]

        # Write each day to influx
        client.write_points(json, time_precision="s")

