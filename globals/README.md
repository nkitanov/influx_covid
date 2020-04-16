# influx_covid_global

Backend calculations and update scripts for https://covid.rally-club.bg/d/covid-global/covid-19-global dashboard.

- `country_list.py` list with countries to update
- `get_data.py` - pull data with [covid library](https://pypi.org/project/covid/) and update influx on regular intervals
- `import_csv.py` - initial update of the db with data from csv files from [John Hopkins repo](https://github.com/CSSEGISandData/COVID-19)
- `rates-single_run.py` - single run to update rate data after initial csv import
- `write_rates.py` - periodic update of daily, weekly, death rates and time to double

There are two Influx measurements which holds the data - `data` and `rates`, here are the schemas in influx line protocol example, region is a tag key:

```data,region=Belgium confirmed=1 recovered=1 active=1 deaths=1 ```

```rates,region=Belgium daily_rate=0.5 weekly_rate=0.5 time2double=10.2 death_rate=0.05```

```
name: data
time                 active confirmed deaths recovered region
----                 ------ --------- ------ --------- ------
2020-04-05T00:00:00Z 14493  19691     1447   3751      Belgium
2020-04-05T00:00:00Z 43264  48436     4943   229       United Kingdom
2020-04-05T00:00:00Z 1243   1308      37     28        Ukraine
2020-04-05T00:00:00Z 310005 337072    9619   17448     US
2020-04-05T00:00:00Z 13970  21100     715    6415      Switzerland
```

```
name: rates
time                 daily_rate death_rate region         time2double weekly_rate
----                 ---------- ---------- ------         ----------- -----------
2020-04-05T00:00:00Z 0.76                  Belgium        8
2020-04-05T00:00:00Z 1.57                  United Kingdom 6
2020-04-05T00:00:00Z 0.54                  Ukraine        5
2020-04-05T00:00:00Z 0.85                  US             6
2020-04-05T00:00:00Z 0.66                  Switzerland    12
```