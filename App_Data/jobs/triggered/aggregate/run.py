#!/usr/bin/env python

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

def json_file_writer(fileName, function):
    """
    Open `fileName` and load it as JSON. Call `function` and write the mutated `data` variable into the original file
    """
    with open(os.path.join(target_folder, fileName), 'r+') as data_file:
        data = json.load(data_file)

        function(data)

        data_file.seek(0)
        json.dump(data, data_file, indent=4)
        data_file.truncate()

def aggregate_list_sum(data, groupKey, sumKey, ignoreKeys = None):
    """
    Loop through a list and sum up the `sumKey` values while treating `groupKey` as a unique ID. The `ignoreKeys` allows
    for a list of keys to ignore and not return
    """
    output = {}

    for item in data:
        key = item[groupKey]

        if ignoreKeys is not None and key in ignoreKeys:
            continue

        if key not in output:
            output[key] = item
            output[key][sumKey] = int(output[key][sumKey])
        else:
            output[key][sumKey] += int(item[sumKey])

    return [ output[item] for item in output]

def aggregate_list_sum_file(fileName, groupKey, sumKey, ignoreKeys = None, sort = None):

    def action(data):
        finalData = aggregate_list_sum(data['data'], groupKey, sumKey, ignoreKeys)

        if sort is not None:
            finalData = sorted(finalData, key = sort)

        data['data'] = finalData[0:min(len(finalData), data['query']['max-results'])]

    json_file_writer(fileName, action)


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
# -----

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


# Sum up the realtime active users for all domains and aggregate them
def aggregateRealtimeJson(data):
    active_visitors = 0

    for site in data['data']:
        active_visitors += int(site['active_visitors'])

    data['data'] = [{ "active_visitors": active_visitors }]

json_file_writer('realtime.json', aggregateRealtimeJson)


# Cities + Countries Realtime aggregation
sortCountKey = lambda x: (-int(x[sumKey]), x[groupByKey])
ignoreKeys = [ 'zz' ]

groupByKey = 'city'
sumKey = 'active_visitors'
aggregate_list_sum_file('top-cities-realtime.json', groupByKey, sumKey, ignoreKeys, sortCountKey)

groupByKey = 'country'
aggregate_list_sum_file('top-countries-realtime.json', groupByKey, sumKey, ignoreKeys, sortCountKey)


# Today.json aggregation
groupByKey = 'hour'
sumKey = 'visits'
aggregate_list_sum_file('today.json', groupByKey, sumKey, None, lambda x: int(x[groupByKey]))
aggregate_list_sum_file('last-48-hours.json', groupByKey, sumKey, None, lambda x: int(x[groupByKey]))