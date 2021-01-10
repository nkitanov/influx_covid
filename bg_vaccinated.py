#!/usr/bin/env python3

from influx_connection import client
from bs4 import BeautifulSoup
from datetime import date, datetime
import requests
import yaml

# Население към 31.12.2019
population_yaml = """
    Благоевград: 
        population: 302694
        name: Blagoevgrad
    Бургас:
        population: 409265
        name: Burgas
    Варна: 
        population: 469885
        name: Varna
    Велико Търново:
        population: 232568
        name: Veliko Tarnovo
    Видин:
        population: 82835
        name: Vidin
    Враца: 
        population: 159470
        name: Vratsa
    Габрово:
        population: 106598
        name: Gabrovo
    Добрич:
        population: 171809
        name: Dobrich
    Кърджали:
        population: 158204
        name: Kardzhali
    Кюстендил:
        population: 116915
        name: Kazanlak
    Ловеч:
        population: 122546
        name: Lovech
    Монтана:
        population: 127001
        name: Montana
    Пазарджик:
        population: 252776
        name: Pazardzhik
    Перник:
        population: 119190
        name: Pernik
    Плевен:
        population: 236305
        name: Pleven
    Пловдив:
        population: 666801
        name: Plovdiv
    Разград:
        population: 110789
        name: Razgrad
    Русе:
        population: 215477
        name: Ruse
    Силистра:
        population: 108018
        name: Silistra
    Сливен:
        population: 184119
        name: Sliven
    Смолян:
        population: 103532
        name: Smolyan
    София:
        population: 226671
        name: Sofia-obl
    София (столица):
        population: 1328790
        name: Sofia-town
    Стара Загора:
        population: 313396
        name: Stara Zagora
    Търговище:
        population: 110914
        name: Targovishte
    Хасково:
        population: 225317
        name: Haskovo
    Шумен:
        population: 172262
        name: Shumen
    Ямбол:
        population: 117335
        name: Yambol
    Общо:
        population: 6951482
        name: Total
"""

URL = "https://coronavirus.bg/bg/statistika"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
population_data = yaml.safe_load(population_yaml)
time = date.today().strftime("%Y-%m-%d") + "T00:00:00Z"
utc_hour = int(datetime.utcnow().strftime("%H"))

s = soup.find("div", attrs={"class": "container-fluid main-content"})
raw_data = (
    s.find(attrs={"class": "row"})
    .find_all(attrs={"class": "col stats"})[2]
    .find_all("td")
)

# List total vaccinated data as dict
# {'Blagoevgrad': 630, 'Burgas': 782, 'Varna': 800, 'Veliko Tarnovo': 555 ...
def data_total():
    index = 0
    d = {}
    while index < len(raw_data):
        d[population_data[raw_data[index].text]["name"]] = int(raw_data[index + 1].text)
        index += 3
    return d


# List data as percent of polulation as dict
def data_percent():
    index = 0
    d = {}
    while index < len(raw_data):
        d[population_data[raw_data[index].text]["name"]] = round(
            int(raw_data[index + 1].text)
            / population_data[raw_data[index].text]["population"],
            4,
        )
        index += 3
    return d


json_total = [
    {"measurement": "bg_vaccinated_total", "time": time, "fields": data_total(),},
]

json_percent = [
    {"measurement": "bg_vaccinated_percent", "time": time, "fields": data_percent(),}
]

if utc_hour < 21:
    client.write_points(json_total)
    client.write_points(json_percent)
