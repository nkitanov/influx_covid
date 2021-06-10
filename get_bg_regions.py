#!/usr/bin/env python3

from opendata import Opendata
from influx_connection import client
from datetime import date
import yaml


# Население към 31.12.2020
population_yaml = """
    BLG_ALL: 
        population: 301138
        name: Blagoevgrad
    BGS_ALL:
        population: 409750
        name: Burgas
    VAR_ALL: 
        population: 470124
        name: Varna
    VTR_ALL:
        population: 229718
        name: Veliko Tarnovo
    VID_ALL:
        population: 81212
        name: Vidin
    VRC_ALL: 
        population: 157637
        name: Vratsa
    GAB_ALL:
        population: 105788
        name: Gabrovo
    DOB_ALL:
        population: 170298
        name: Dobrich
    KRZ_ALL:
        population: 160781
        name: Kardzhali
    KNL_ALL:
        population: 116619
        name: Kyustendil
    LOV_ALL:
        population: 122490
        name: Lovech
    MON_ALL:
        population: 125395
        name: Montana
    PAZ_ALL:
        population: 251300
        name: Pazardzhik
    PER_ALL:
        population: 120426
        name: Pernik
    PVN_ALL:
        population: 233438
        name: Pleven
    PDV_ALL:
        population: 666398
        name: Plovdiv
    RAZ_ALL:
        population: 109810
        name: Razgrad
    RSE_ALL:
        population: 212729
        name: Ruse
    SLS_ALL:
        population: 106852
        name: Silistra
    SLV_ALL:
        population: 182551
        name: Sliven
    SML_ALL:
        population: 101887
        name: Smolyan
    SFO_ALL:
        population: 238476
        name: Sofia-obl
    SOF_ALL:
        population: 1308412
        name: Sofia-town
    SZR_ALL:
        population: 311400
        name: Stara Zagora
    TGV_ALL:
        population: 110027
        name: Targovishte
    HKV_ALL:
        population: 223625
        name: Haskovo
    SHU_ALL:
        population: 171781
        name: Shumen
    JAM_ALL:
        population: 116486
        name: Yambol
    TOTAL:
        population: 6916548
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
