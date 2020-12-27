import requests

class Opendata:
    def __init__(self, resource_uri):
        r = requests.post('https://data.egov.bg/api/getResourceData', {'resource_uri': resource_uri})
        api_call = r.json()

        if api_call['success'] == True:
            self.full_data = api_call['data'] # Full data excl. status messages
        else:
            print('There is error:', api_call)
            exit()

    def columns(self):
        # Return dictionary of columns items indexes
        cols = self.full_data[0]
        columns = {}
        for x in range(len(cols)):
            columns[cols[x]] = x
        return(columns)

    def data(self, col='all', date=''):
        # Return all data or specific column + date
        if col == 'all':
            return self.full_data[1:]
        else:
            index = self.columns()[col]
            d = {}
            for item in self.full_data[1:]:
                if len(date) == 0:
                    d[item[0]] = item[index]
                elif date == item[0]:
                    d[item[0]] = item[index]
            return(d)