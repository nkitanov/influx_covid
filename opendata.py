import requests

class Opendata:
    def __init__(self, resource_uri):
        api_call = requests.post('https://data.egov.bg/api/getResourceData', {'resource_uri': resource_uri})
        self.full_data = api_call.json()

        if self.full_data['success'] != True:
            print('There is error:')
            print(self.full_data)

    def columns(self):
        # Return dictionary of column index
        cols = self.full_data['data'][0]
        columns = {}
        for x in range(len(cols)):
            columns[cols[x]] = x
        return(columns)

    def data(self, col='all'):
        if col == 'all':
            return self.full_data['data'][1:]
        else:
            index = self.columns()[col]
            d = {}
            for item in self.full_data['data'][1:]:
                d[item[0]] = item[index]
            return(d)