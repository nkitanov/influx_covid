
from influxdb import InfluxDBClient

client = InfluxDBClient(host="192.168.1.201", port=8086, database="home_assistant")

# Build list with all days
q = client.query("select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' and time > '2020-03-11T00:00:00Z'  group by time(1d)", epoch='s')
data = []
for i in q.get_points():
    data.append(i)

for x in data:
    dateh = x["time"]
    half_value =str(x["last"] / 2)
    if float(half_value) <= 3.5: # skip it for the first days
         continue

    q = client.query("select last(value) from people where entity_id='bulgaria_coronavirus_confirmed' and value < " + half_value + "", epoch='s')
    list = []
    for i in q.get_points():
        list.append(i)
    datel = list[0]["time"]
    
    days = round((dateh - datel) / 86400, 1) 

    json = [{"fields": {"value": days}, "measurement": "covid_timedouble", "time": dateh}]
    client.write_points(json, time_precision='s')
