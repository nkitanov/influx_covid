# influx_covid_global

Backend calculations and update scripts for https://covid.rally-club.bg/d/covid-global/covid-19-global dashboard.

- `Covid-19 Global.json` - Grafana Dashboard config
- `country_list.py` list with countries to update
- `get_data.py` - pull data with [covid library](https://pypi.org/project/covid/) and update influx on regular intervals
- `import_csv.py` - initial update of the db with data from csv files from [John Hopkins CSV files](https://github.com/CSSEGISandData/COVID-19)
- `rates-single_run.py` - single run to update rate data after initial csv import
- `write_rates.py` - periodic update of daily, weekly, death rates and time to double

There are two Influx measurements which holds the data - `data` and `rates`, here are the schemas in influx line protocol example, **region is a tag key**:

```data,region=Belgium confirmed=1,recovered=1,active=1,deaths=1,tested=42343,population=11583739```

```rates,region=Belgium daily_rate=0.5,weekly_rate=0.5,time2double=10.2,death_rate=0.05,death_pm=50.2,tested_milion=12034,tested_confirmed=10,projected_positives=324422,projected_positives_percent=3.23```

```
name: data
time       active  confirmed deaths population recovered region  tested
----       ------  --------- ------ ---------- --------- ------  ------
1589878203 2669945 4907135   320392            1916798   Global  61397076
1589877795 220974  299941    2837   145927292  76130     Russia  7352316
1589877794 5982    17036     1124   19251921   9930      Romania 313621
1589877794 5669    10699     231    8741321    4799      Serbia  185385
1589877794 1297    2836      165    10428746   1374      Greece  131684

```

```
name: rates
time       daily_rate death_pm death_rate projected_positives projected_positives_percent region      tested_confirmed tested_milion time2double weekly_rate
----       ---------- -------- ---------- ------------------- --------------------------- ------      ---------------- ------------- ----------- -----------
1589878209            58.38    6.6                                                        Romania
1589878208                                596058055           7.69                        Global      13               7923
1589878208                                2447213             14.29                       Netherlands 7                17358
1589878208            218.11   6.16                                                       Switzerland
1589877794                                                                                Turkey                                     33.4

```