#!/usr/bin/env python3

import requests
import json
import datetime
from influx_connection import client

# Get data from API of https://data.egov.bg/data/resourceView/8f62cfcf-a979-46d4-8317-4e1ab9cbd6a8
url = "https://data.egov.bg/api/getResourceData"
json_params = {"resource_uri": "8f62cfcf-a979-46d4-8317-4e1ab9cbd6a8"}
r = requests.post(url, data=json_params)
data = json.loads(r.text)
today_month = datetime.datetime.now().month

# Generate json body with influx data
for day in data["data"][1:]:
    time = day[0].replace("/", "-") + "T00:00:00Z"  # Time in influx format
    month = int(day[0].split("/")[1])
    # Push only current month values to speed up (comment this if to upload all)
    if today_month != month:
        continue
    json = [
        {
            "measurement": "bg_age_groups",
            "time": time,
            "fields": {
                "0-19": int(day[1]),
                "20-29": int(day[2]),
                "30-39": int(day[3]),
                "40-49": int(day[4]),
                "50-59": int(day[5]),
                "60-69": int(day[6]),
                "70-79": int(day[7]),
                "80-89": int(day[8]),
                "90+": int(day[9]),
            },
        }
    ]
    # Write in influx
    client.write_points(json)
