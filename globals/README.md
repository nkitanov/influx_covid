# influx_covid_global

Backend calculations and update scripts for https://covid.rally-club.bg/d/covid-global/covid-19-global dashboard.

- `Covid-19 Global.json` - Grafana Dashboard config
- `country_list.py` list with countries to update
- `get_data.py` - pull data with [covid library](https://pypi.org/project/covid/) and update influx on regular intervals
- `import_csv.py` - initial update of the db with data from csv files from [John Hopkins repo](https://github.com/CSSEGISandData/COVID-19)
- `rates-single_run.py` - single run to update rate data after initial csv import
- `write_rates.py` - periodic update of daily, weekly, death rates and time to double

There are two Influx measurements which holds the data - `data` and `rates`, here are the schemas in influx line protocol example, region is a tag key:

```data,region=Belgium confirmed=1 recovered=1 active=1 deaths=1 ```

```rates,region=Belgium daily_rate=0.5 weekly_rate=0.5 time2double=10.2 death_rate=0.05 death_pm=50.2```

```
name: data
time                           active confirmed deaths recovered region
----                           ------ --------- ------ --------- ------
2020-04-15T07:49:08.037606841Z 56115  132210    3495   72600     Germany
2020-04-15T07:49:08.538556489Z 594    735       36     105       Bulgaria
2020-04-15T07:49:08.991404679Z 7101   8100      146    853       Japan
2020-04-15T07:49:09.250958065Z 1740   83351     3346   78265     China
2020-04-15T07:49:10.879540113Z 86491  131362    15750  29121     France

```

```
name: rates
time                           daily_rate death_pm death_rate region  time2double weekly_rate
----                           ---------- -------- ---------- ------  ----------- -----------
2020-04-20T17:55:14.159330486Z                                Global              0.71
2020-04-20T17:55:13.390983368Z                                US                  0.63
2020-04-20T17:55:12.634030322Z            55.89    3.2        Germany
2020-04-20T17:55:12.530394013Z                                Germany             0.54
2020-04-20T17:55:11Z                                          Global  16.7
```