#!/usr/bin/env python

import itertools
import json
import os

report_folder = 'data'
target_folder = report_folder

def merge_dict_into(objOne, objTwo):
    """
    Add keys from objTwo that do not exist in objOne to objOne
    """
    missingKeys = [ key for key in objTwo if key not in objOne ]

    for key in missingKeys:
        objOne[key] = objTwo[key]

def merge_dict_addition(objOne, objTwo):
    """
    Merge two objects and add the respective values to get a total of both
    """
    for key in objOne:
        try:
            if isinstance(objOne[key], (int, list, tuple)):
                objOne[key] += objTwo[key]
            elif isinstance(objOne[key], dict):
                merge_dict_addition(objOne[key], objTwo[key])
        except KeyError:
            pass

def aggregate_list_dicts_sum(dataList, groupByKey, addByKey, sortBy=None):
    cityData = []
    cities = sorted(dataList, key=lambda x: x[groupByKey])

    for key, group in itertools.groupby(cities, lambda x: x[groupByKey]):
        if key == 'zz':
            continue

        obj = {}
        obj[groupByKey] = key
        obj[addByKey] = sum([int(item[addByKey]) for item in group])

        cityData.append(obj)

    if sortBy == None:
        cityData = sorted(cityData, key=lambda x: (-int(x[addByKey]), x[groupByKey]))
    else:
        cityData = sorted(cityData, key=lambda x: (int(x[sortBy])))

    return cityData[0:min(len(cityData), data['query']['max-results'])]

# Get all of our agencies and deleted the first item in the list. The first item is a collection
# of everything in the folder and is safe to skip
agencies = [ agency for agency in os.walk(report_folder) ]
del agencies[0]

# Get all of the reports in the first agency's folder. Since all agencies have the same reports generated,
# we'll be fine
reports = agencies[0]

# With the aggregation, the sorting is lost, so sort these reports' `data` array by the respective key
sortBy = {
    "top-pages-7-days.json": "visits",
    "top-pages-30-days.json": "visits",
    "top-pages-realtime.json": "active_visitors"
}

# Aggregate all of the reports
for report in reports[2]:
    if not report.endswith(".json"):
        continue

    jsonData = []

    for agency in agencies:
        reportFile = os.path.join(agency[0], report)

        try:
            with open(reportFile) as file_content:
                data = json.load(file_content)

                if not jsonData:
                    jsonData = data
                    continue

                merge_dict_into(jsonData, data)

                try:
                    jsonData['data'] += data['data']
                except KeyError:
                    pass

                try:
                    merge_dict_addition(jsonData['totals'], data['totals'])
                except KeyError:
                    pass

        except IOError:
            pass

    try:
        sortedData = sorted(jsonData['data'], key=lambda x: -int(x[sortBy[report]]))
        jsonData['data'] = sortedData[0:min(len(sortedData), jsonData['query']['max-results'])]
    except KeyError:
        pass

    with open(os.path.join(target_folder, report), 'w+') as results_file:
        json.dump(jsonData, results_file, indent=4)


# Reports that need further, special, aggregation
# -----

# Consolidate the count of all of the domains
with open(os.path.join(target_folder, 'realtime.json'), 'r+') as data_file:
    data = json.load(data_file)
    active_visitors = 0

    for site in data['data']:
        active_visitors += int(site['active_visitors'])

    data['data'] = [{ "active_visitors": active_visitors }]

    data_file.seek(0)
    json.dump(data, data_file, indent=4)
    data_file.truncate()

def aggregate_list_dict_files(fileName, groupByKey, addByKey, sortBy = None):
    with open(os.path.join(target_folder, fileName), 'r+') as data_file:
        data = json.load(data_file)

        data['data'] = aggregate_list_dicts_sum(data['data'], groupByKey, addByKey, sortBy)

        data_file.seek(0)
        json.dump(data, data_file, indent=4)
        data_file.truncate()

aggregate_list_dict_files('top-cities-realtime.json', 'city', 'active_visitors')
aggregate_list_dict_files('top-countries-realtime.json', 'country', 'active_visitors')
aggregate_list_dict_files('today.json', 'hour', 'visits', 'hour')