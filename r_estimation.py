#!/usr/bin/env python3

from country_list import country_list
from influx_connection import client
from datetime import date, datetime, timedelta

generation_time = 4  # Time between 7 days intervals
today = date.today().strftime("%Y-%m-%d") + "T00:00:00Z"


def diff_ranges(d):
    try:
        result = int(d[0]["last"] - d[-1]["last"])
    except TypeError:
        result = 0
    return result


def day_back(date):
    # Subtract 1 day and return influx format as the R estimation is correct for the previous day
    return (
        datetime.strptime(date.split("T")[0], "%Y-%m-%d") - timedelta(days=1)
    ).strftime("%Y-%m-%d") + "T00:00:00Z"


def estimate(country):
    # Return dict with estimations: {'2021-02-14T00:00:00Z': 1.082, '2021-02-13T00:00:00Z': 1.129}
    q = client.query(
        "select last(confirmed) from data where region='"
        + country
        + "'group by time(1d) order by time desc"
    )
    points_list = list(q.get_points())
    index = 0
    d = {}

    while index < len(points_list):
        start_1 = index
        end_1 = index + 8
        start_2 = start_1 + generation_time
        end_2 = start_2 + 8

        if end_2 < len(points_list):
            try:
                d[points_list[index]["time"]] = round(
                    diff_ranges(points_list[start_1:end_1])
                    / diff_ranges(points_list[start_2:end_2]),
                    3,
                )
            except ZeroDivisionError or TypeError:
                d[points_list[index]["time"]] = 0
        index += 1
        if index > 2:  # List only last few dates
            break
    return d


for country in country_list:
    json = [
        {
            "measurement": "data",
            "tags": {"region": country},
            "time": day_back(today),
            "fields": {"r_estim": estimate(country)[today]},
        }
    ]
    client.write_points(json)

