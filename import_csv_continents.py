# Script to parse csv files from https://github.com/CSSEGISandData/COVID-19
# and push the data to Influxdb
# Edit variables for your env

import csv
import os
from datetime import datetime
from influxdb import InfluxDBClient
from country_list import continents_dictionary

client = InfluxDBClient(host="35.207.86.81", port=8086, database="covid_global")

# Path to csv files
path = "C:/Users/nki/git/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
dir_list = list(os.scandir(path))


def date_convert(csv_date):
    epoch_date = int(
        datetime.strptime(csv_date, "%m-%d-%Y").timestamp() + 10800
    )  # Shift time forward to be 00:00 GMT
    return epoch_date


def get_numbers_country(csv_loc, country):
    # Function return dictionary like, time in UNIX seconds based on file name date
    # {'confirmed': 15348, 'recovered': 2495, 'deaths': 1011, 'active': 14337, 'time': 1585774800, 'region': 'Belgium'}
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


# Calculate per continent values as defined in continents_dictionary
continents = [continent for continent in continents_dictionary]

for continent in continents:
    country_list_cont = continents_dictionary[continent]

    for f in dir_list:
        confirmed = 0
        recovered = 0
        active = 0
        deaths = 0
        for country in country_list_cont:
            if country == "USA":
                country = "US"
            if country == "UK":
                country = "United Kingdom"
            csv_loc = path + f.name
            csv_date = (os.path.splitext(csv_loc)[0]).split("/")[-1]
            d = get_numbers_country(csv_loc, country)
            confirmed += d["confirmed"]
            recovered += d["recovered"]
            active += d["active"]
            deaths += d["deaths"]
            date = csv_date

        json = [
            {
                "measurement": "data",
                "tags": {"region": continent},
                "time": date,
                "fields": {
                    "confirmed": confirmed,
                    "recovered": recovered,
                    "active": active,
                    "deaths": deaths,
                },
            }
        ]

        # Write each day to influx
        client.write_points(json, time_precision="s")
        print(json)
