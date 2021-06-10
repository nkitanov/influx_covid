#!/usr/bin/env python3

from influx_connection import client
from bs4 import BeautifulSoup
from datetime import date, datetime
import requests
import yaml
from get_bg_regions import population_data

town_map = """
BLG_ALL: Благоевград
BGS_ALL: Бургас
VAR_ALL: Варна
VTR_ALL: Велико Търново
VID_ALL: Видин
VRC_ALL: Враца
GAB_ALL: Габрово
DOB_ALL: Добрич
KRZ_ALL: Кърджали
KNL_ALL: Кюстендил
LOV_ALL: Ловеч
MON_ALL: Монтана
PAZ_ALL: Пазарджик
PER_ALL: Перник
PVN_ALL: Плевен
PDV_ALL: Пловдив
RAZ_ALL: Разград
RSE_ALL: Русе
SLS_ALL: Силистра
SLV_ALL: Сливен
SML_ALL: Смолян
SFO_ALL: София
SOF_ALL: София (столица)
SZR_ALL: Стара Загора
TGV_ALL: Търговище
HKV_ALL: Хасково
SHU_ALL: Шумен
JAM_ALL: Ямбол
"""

URL = "https://coronavirus.bg/bg/statistika"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
time = date.today().strftime("%Y-%m-%d") + "T00:00:00Z"
utc_hour = int(datetime.utcnow().strftime("%H"))

s = soup.find("div", attrs={"class": "container-fluid main-content"})
raw_data = (
    s.find(attrs={"class": "row"})
    .find_all(attrs={"class": "col stats"})[0]
    .find_all("td")
)

# Use population data from get_bg_regions and map the names
town_map = yaml.safe_load(town_map)
population_dict = {}
for region in population_data:
    if region != "TOTAL":
        population_dict[town_map[region]] = {
            "population": population_data[region]["population"],
            "name": population_data[region]["name"],
        }
    else:
        population_dict["Общо"] = {
            "population": population_data["TOTAL"]["population"],
            "name": "Total",
        }

# List total vaccinated data as dict
# {'Blagoevgrad': {'total': 842, 'total_doses': 177},
def data_total():
    index = 0
    d = {}
    while index < len(raw_data):
        total = raw_data[index + 1].text
        total_doses = raw_data[index + 6].text
        if total == "-":
            total = 0
        d[population_dict[raw_data[index].text]["name"]] = {
            "total": int(total),
            "total_doses": int(total_doses),
        }
        index += 7
    return d


# List vaccinated with second dose as percent of polulation as dict
# {'Blagoevgrad': 0.0028, 'Burgas': 0.0026, 'Varna': 0.0037, 'Veliko Tarnovo': 0.0027 ...
def data_percent():
    index = 0
    d = {}
    while index < len(raw_data):
        d[population_dict[raw_data[index].text]["name"]] = round(
            int(raw_data[index + 6].text)
            / population_dict[raw_data[index].text]["population"],
            4,
        )
        index += 7
    return d


def data_second_dose():
    d = {}
    for region in population_dict:
        en_name = population_dict[region]["name"]
        d[en_name] = data_total()[en_name]["total_doses"]
    return d


# Generate simplified dict for import totals in influx as the data_total function provides more data
data_all = {}
for region in population_dict:
    data_all[population_dict[region]["name"]] = data_total()[
        population_dict[region]["name"]
    ]["total"]

json_total = [
    {
        "measurement": "bg_vaccinated_total",
        "time": time,
        "fields": data_all,
    },
]

json_percent = [
    {
        "measurement": "bg_vaccinated_percent",
        "time": time,
        "fields": data_percent(),
    }
]

json_second_dose = [
    {
        "measurement": "bg_vaccinated_second",
        "time": time,
        "fields": data_second_dose(),
    }
]

if utc_hour < 21:
    client.write_points(json_total)
    client.write_points(json_percent)
    client.write_points(json_second_dose)
