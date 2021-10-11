#!/usr/bin/env python3

from influx_connection import client
from opendata import Opendata

# Until 31.12.2020 per 100k
population_data = {
    "total": 6916548 / 100000,
    "0-1": 59029 / 100000,
    "1-5": 255341 / 100000,
    "6-9": 337290 / 100000,
    "10-14": 347354 / 100000,	
    "15-19": 314238 / 100000,
    "0-19": 1313252 / 100000,
    "20-29": 670806 / 100000,
    "30-39": 953393 / 100000,
    "40-49": 1050347 / 100000,
    "50-59": 956606 / 100000,
    "60-69": 919675 / 100000,
    "70-79": 716566 / 100000 ,
    "80-89": 298212 / 100000,
    "90+": 37691 / 100000,
}

# Get data from API
opendata = Opendata("8f62cfcf-a979-46d4-8317-4e1ab9cbd6a8")
data = opendata.data()

# Generate json body with influx data for the last 1w only
for record in data[-7:]:
    total = 0
    day = [ '0' if x == '-' else x for x in record ]
    time = day[0].replace("/", "-") + "T00:00:00Z"  # Time in influx format
    
    for num in day[1:]:
        total += int(num)

    json = [
        {
            "measurement": "bg_age_groups",
            "time": time,
            "fields": {
                "0-1": round(int(day[1]) / population_data['0-1']),
                "1-5": round(int(day[2]) / population_data['1-5']),
                "6-9": round(int(day[3]) / population_data['6-9']),
                "10-14": round(int(day[4]) / population_data['10-14']), 	
                "15-19": round(int(day[5]) / population_data['15-19']),
                "0-19":  round(int(day[6]) / population_data['0-19']),
                "20-29": round(int(day[7]) / population_data['20-29']),
                "30-39": round(int(day[8]) / population_data['30-39']),
                "40-49": round(int(day[9]) / population_data['40-49']),
                "50-59": round(int(day[10]) / population_data['50-59']),
                "60-69": round(int(day[11]) / population_data['60-69']),
                "70-79": round(int(day[12]) / population_data['70-79']),
                "80-89": round(int(day[13]) / population_data['80-89']),
                "90+":   round(int(day[14]) / population_data['90+']),
                "total": round(total / population_data['total'])
            },
        }
    ]
    # Write in influx
    client.write_points(json)