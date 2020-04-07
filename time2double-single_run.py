
from influxdb import InfluxDBClient
from datetime import date

client = InfluxDBClient(host="192.168.1.201", port=8086, database="home_assistant")

# Build list with all days
q = client.query("select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' and time > '2020-03-11T00:00:00Z'  group by time(1d)")
data = []
for i in q.get_points():
    data.append(i)

for x in data:
    dateh = x["time"].split("T")[0].split("-")
    yearh = int(dateh[0])
    monthh = int(dateh[1])
    dayh = int(dateh[2])
    half_value =str(x["last"] / 2)
    if float(half_value) <= 3.5: # skip it for the first days
        continue

    q = client.query("select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' and value < " + half_value + "" )
    list = []
    for i in q.get_points():
        list.append(i)
    datel = list[0]["time"].split("T")[0].split("-")
    yearl = int(datel[0])
    monthl = int(datel[1])
    dayl = int(datel[2])
    
    diff = (date(yearh, monthh, dayh) - date(yearl, monthl, dayl)).days
    date_db = (str(yearh) + "-" + str(monthh) + "-" + str(dayh))

    json = [{"fields": {"value": diff}, "measurement": "covid_timedouble", "time": date_db}]
    client.write_points(json)
