from influxdb import InfluxDBClient

client = InfluxDBClient(host='192.168.1.201', port=8086, database='home_assistant')


def diff():
    avg_list = []
    avg=client.query('select * from covid_confirmed_average;')
    for i in avg.get_points():
        avg_list.append(i)
    fin = avg_list[-1]['last']
    prev = avg_list[-2]['last']
    return float(fin-prev)

def rate():
    rate = []
    dq=client.query('select * from covid_confirmed_average;')
    for i in dq.get_points():
        rate.append(i)
    first = rate[-1]['last']
    second = rate[-2]['last']
    third = rate[-3]['last']
    print(first, second, third)
    return round((first-second)/(second-third), 2)

print(rate())

# json_diff = [{'fields': {'value': diff()}, 'measurement': 'covid_confirmed_diff'}]
# json_rate = [{'fields': {'value': rate()}, 'measurement': 'covid_confirmed_rate'}]
# client.write_points(json_diff)
# client.write_points(json_rate)