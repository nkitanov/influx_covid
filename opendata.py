import requests


class Opendata:
    def __init__(self, resource_uri):
        r = requests.post(
            "https://data.egov.bg/api/getResourceData", {"resource_uri": resource_uri}
        )
        api_call = r.json()

        if api_call["success"] == True:
            self.full_data = api_call["data"]  # Full data excl. status messages
        else:
            print("There is error:", api_call)
            exit()

    def columns(self):
        # Return dictionary of columns items indexes
        cols = self.full_data[0]
        columns = {}
        for x in range(len(cols)):
            columns[cols[x]] = x
        return columns

    def data(self, col="all", date=""):
        # Return all data or specific column + date
        if col == "all":
            return self.full_data[1:]
        else:
            index = self.columns()[col]
            d = {}
            for item in self.full_data[1:]:
                if len(date) == 0:
                    d[item[0]] = item[index]
                elif date == item[0]:
                    d[item[0]] = item[index]
            return d

    def total(self):
        # Return totals of ALL colums per day in dict format:
        # {'2020-06-06': 2668, '2020-06-07': 2711, '2020-06-08': 2727}
        d = {}

        # Generate index of columns with all data excluding active
        cols = []
        for col in self.columns():
            if "ALL" in col:
                cols.append(self.columns()[col])

        for line in self.full_data[1:]:
            line_sum = []
            for item in cols:
                line_sum.append(line[item])
            d[line[0].replace("/", "-")] = sum(list(map(int, line_sum)))
        return d
