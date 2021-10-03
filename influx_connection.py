import sys
from influxdb import InfluxDBClient

# Influx host is different if I run it from my Win PC
if sys.platform == "linux":
    influx_host = "localhost"
else:
    influx_host = "192.168.1.30"

client = InfluxDBClient(host=influx_host, port=8086, database="covid_global")