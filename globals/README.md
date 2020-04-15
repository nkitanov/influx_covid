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