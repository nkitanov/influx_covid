#!/usr/bin/env python3

from opendata import Opendata
from influx_connection import client
from datetime import date
import yaml


# Население към 31.12.2019
population_yaml = """
    BLG_ALL: 
        population: 302694
        name: Blagoevgrad
    BGS_ALL:
        population: 409265
        name: Burgas
    VAR_ALL: 
        population: 469885
        name: Varna
    VTR_ALL:
        population: 232568
        name: Veliko Tarnovo
    VID_ALL:
        population: 82835
        name: Vidin
    VRC_ALL: 
        population: 159470
        name: Vratsa
    GAB_ALL:
        population: 106598
        name: Gabrovo
    DOB_ALL:
        population: 171809
        name: Dobrich
    KRZ_ALL:
        population: 158204
        name: Kardzhali
    KNL_ALL:
        population: 116915
        name: Kyustendil
    LOV_ALL:
        population: 122546
        name: Lovech
    MON_ALL:
        population: 127001
        name: Montana
    PAZ_ALL:
        population: 252776
        name: Pazardzhik
    PER_ALL:
        population: 119190
        name: Pernik
    PVN_ALL:
        population: 236305
        name: Pleven
    PDV_ALL:
        population: 666801
        name: Plovdiv
    RAZ_ALL:
        population: 110789
        name: Razgrad
    RSE_ALL:
        population: 215477
        name: Ruse
    SLS_ALL:
        population: 108018
        name: Silistra
    SLV_ALL:
        population: 184119
        name: Sliven
    SML_ALL:
        population: 103532
        name: Smolyan
    SFO_ALL:
        population: 226671
        name: Sofia-obl
    SOF_ALL:
        population: 1328790
        name: Sofia-town
    SZR_ALL:
        population: 313396
        name: Stara Zagora
    TGV_ALL:
        population: 110914
        name: Targovishte
    HKV_ALL:
        population: 225317
        name: Haskovo
    SHU_ALL:
        population: 172262
        name: Shumen
    JAM_ALL:
        population: 117335
        name: Yambol
    TOTAL:
        population: 6951482
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
                    population_data[town]["name"]: round(
                        int(data_dict[date]) / (population_data[town]['population'] / 100000)
                    ),
                },
            }
        ]
        client.write_points(json)

# Write totals for today
json = [
    {
        "measurement": "bg_regions",
        "time": today.replace('/', '-') + "T00:00:00Z",  # Time in influx format
        "fields": {
            "Total": round(int((opendata.total()[today.replace('/', '-')]) / (population_data['TOTAL']['population'] / 100000))),
        },
    }
]
client.write_points(json)
