#!/usr/bin/env python3

from opendata import Opendata
from influx_connection import client
from datetime import date
import yaml


# Население към 31.12.2019
population_yaml = """
    BLG_ALL: 302694
    BGS_ALL: 409265
    VAR_ALL: 469885
    VTR_ALL: 232568
    VID_ALL: 82835
    VRC_ALL: 159470
    GAB_ALL: 106598
    DOB_ALL: 171809
    KRZ_ALL: 158204
    KNL_ALL: 116915
    LOV_ALL: 122546
    MON_ALL: 127001
    PAZ_ALL: 252776
    PER_ALL: 119190
    PVN_ALL: 236305
    PDV_ALL: 666801
    RAZ_ALL: 110789
    RSE_ALL: 215477
    SLS_ALL: 108018
    SLV_ALL: 184119
    SML_ALL: 103532
    SFO_ALL: 226671
    SOF_ALL: 1328790
    SZR_ALL: 313396
    TGV_ALL: 110914
    HKV_ALL: 225317
    SHU_ALL: 172262
    JAM_ALL: 117335
"""

opendata = Opendata("cb5d7df0-3066-4d7a-b4a1-ac26525e0f0c")
population_data = yaml.safe_load(population_yaml)
today = date.today().strftime("%Y/%m/%d")
region_list = []

# Leave only ALL columns excluding active
for town in opendata.columns():
    if "ALL" in town:
        region_list.append(town)

for town in region_list:
    data_dict = opendata.data(town, today)
    for date in data_dict:
        time = date.replace("/", "-") + "T00:00:00Z"  # Time in influx format
        json = [
            {
                "measurement": "bg_regions",
                "time": time,
                "fields": {
                    town.split("_")[0]: round(
                        int(data_dict[date]) / (population_data[town] / 100000)
                    ),
                },
            }
        ]
        client.write_points(json)

