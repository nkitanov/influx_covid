# influx_covid_global

Backend calculations and update scripts for https://covid.rally-club.bg/d/covid-global/covid-19-global dashboard.

- `Covid-19 Global.json` - Grafana Dashboard config
- `country_list.py` list with countries to update
- `get_data.py` - pull data with [covid library](https://pypi.org/project/covid/) and update influx on regular intervals
- `import_csv.py` - initial update of the db with data from csv files from [John Hopkins repo](https://github.com/CSSEGISandData/COVID-19)
- `rates-single_run.py` - single run to update rate data after initial csv import
- `write_rates.py` - periodic update of daily, weekly, death rates and time to double

There are two Influx measurements which holds the data - `data` and `rates`, here are the schemas in influx line protocol example, **region is a tag key**:

```data,region=Belgium confirmed=1 recovered=1 active=1 deaths=1 tested=42343```

```rates,region=Belgium daily_rate=0.5 weekly_rate=0.5 time2double=10.2 death_rate=0.05 death_pm=50.2 tested_milion=12034 tested_confirmed=10 projected_positives=324422 projected_positives_percent=3.23```

```
name: data
time                           active  confirmed deaths recovered region   tested
----                           ------  --------- ------ --------- ------   ------
2020-04-30T06:40:03.663807311Z 1988125 3221617   228263 1005229   Global   32019440
2020-04-30T06:40:03.626811538Z 8907    10406     261    1238      Ukraine  111859
2020-04-30T06:30:04.188521276Z 1987713 3221044   228252 1005079   Global   32000592
2020-04-30T06:10:04.102715146Z 1990809 3221029   228252 1001968   Global   31999936
2020-04-30T06:10:04.048873973Z 1157    1488      65     266       Bulgaria 45208

```

```
name: rates
time                           daily_rate death_pm death_rate projected_positives projected_positives_percent region  tested_confirmed tested_milion time2double weekly_rate
----                           ---------- -------- ---------- ------------------- --------------------------- ------  ---------------- ------------- ----------- -----------
2020-05-01T12:23:32.051675614Z                                4864482             3.33                        Russia  30               23915
2020-05-01T12:23:31.303513195Z                                1282513             6.67                        Romania 15               9548
2020-05-01T12:23:30.597704393Z                                873737              10                          Serbia  10               9802
2020-05-01T12:23:29.896389538Z                                372252              3.57                        Greece  28               6920
2020-05-01T12:23:29.200419255Z                                9371007             11.11                       Turkey  9                12255

```