#!/usr/bin/env python

import csv
import json
import os
import shutil
import sys
from random import shuffle

# The location where agencies individual data is stored; e.g. each agency has its own folder
if len(sys.argv) > 1:
  report_folder = sys.argv[1]
else:
  report_folder = os.path.join(
    os.environ['HOME'],
    "site",
    "wwwroot",
    os.environ["ANALYTICS_DATA_PATH"]
  )

# Where the aggregated data will go
target_folder = report_folder + "_aggregation"

# Make a temporary folder for data aggregation
if os.path.exists(target_folder):
  shutil.rmtree(target_folder)

os.mkdir(target_folder)

# Reports that will not be aggregated by this script
ignored_reports = [
  'user-activity.json'
]

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
    if not objOne:
    	return objTwo

    if not objTwo:
    	return objOne

    newObj = {}

    for key in objOne:
        try:
            if isinstance(objOne[key], (int, list, tuple)):
                newObj[key] = objOne[key] + objTwo[key]
            elif isinstance(objOne[key], dict):
                newObj[key] = merge_dict_addition(objOne[key], objTwo[key])
        except KeyError:
            pass

    return newObj

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

    return [ output[item] for item in output ]

def aggregate_list_sum_file(fileName, groupKey, sumKey, ignoreKeys = None, sort = None):

    def action(data):
        finalData = aggregate_list_sum(data['data'], groupKey, sumKey, ignoreKeys)

        if sort is not None:
            finalData = sorted(finalData, key = sort)

        data['data'] = finalData[0:min(len(finalData), data['query']['max-results'])]

    json_file_writer(fileName, action)

def aggregate_json_data(jsonFile, primaryKey, uniqueKey, sumKey, fieldnames, sort = None):

  def action(data):
    primaryKeys = list({ item[primaryKey] for item in data['data'] })
    totals = []

    for pKey in primaryKeys:
      items = [ item for item in data['data'] if item[primaryKey] == pKey ]
      totals += aggregate_list_sum(items, uniqueKey, sumKey)

    data['data'] = sorted(totals, key = sort)

  json_file_writer(jsonFile, action)

def csv_file_writer(fileName, data, fieldnames, sort = None):
  csvFile = os.path.join(target_folder, os.path.splitext(os.path.basename(fileName))[0] + '.csv')

  with open(csvFile, 'wb+') as csv_file:
    csvwriter = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csvwriter.writeheader()

    [ csvwriter.writerow(item) for item in sorted(data, key=sort) ]

def aggregate_csv_data(jsonFile, fieldnames, sort = None):

  with open(os.path.join(target_folder, jsonFile)) as data_file:
    data = json.load(data_file)

    csv_file_writer(jsonFile, data['data'], fieldnames, sort)


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

# These keys need to be stripped from the respective reports
stripKeys = {
    "top-countries-realtime.json": ['domain'],
    "top-cities-realtime.json": ['domain']
}


# Aggregate all of the reports
# -----

for report in reports[2]:
    if not report.endswith(".json") or report in ignored_reports:
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
                    jsonData['totals'] = merge_dict_addition(jsonData['totals'], data['totals'])
                except KeyError:
                    pass

        except IOError:
            pass

    try:
        sortKey = sortBy[report]
        sortedData = sorted(jsonData['data'], key=lambda x: -int(x[sortKey]))

        moreThanOneViewer = [item for item in sortedData if int(item[sortKey]) > 1]
        onlyOneViewer = [item for item in sortedData if int(item[sortKey]) == 1]

        shuffle(onlyOneViewer)
        sortedData = moreThanOneViewer + onlyOneViewer

        jsonData['data'] = sortedData[0:min(len(sortedData), jsonData['query']['max-results'])]
    except KeyError:
        pass

    if report in stripKeys:
        for item in jsonData['data']:
            for key in stripKeys[report]:
                del item[key]

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
sortCountKey = lambda x: int(x[groupByKey])
groupByKey = 'hour'
ignoreKeys = None
sumKey = 'visits'
aggregate_list_sum_file('today.json', groupByKey, sumKey, ignoreKeys, sortCountKey)
aggregate_list_sum_file('last-48-hours.json', groupByKey, sumKey, ignoreKeys, sortCountKey)


# Aggregate `users.json`
aggregate_list_sum_file('users.json', 'date', 'visits', None, lambda x: x['date'])


# CSV aggregation
# -----


# All of these reports have similar data structures
aggregationDefinitions = {
  'browsers.json': 'browser',
  'devices.json': 'device',
  'ie.json': 'browser_version',
  'os.json': 'os',
  'windows.json': 'os_version'
}

for k in aggregationDefinitions:
  v = aggregationDefinitions[k]
  sorting = lambda x: (x['date'], -int(x['visits']))

  aggregate_json_data(k, 'date', v, 'visits', ['date', v, 'visits'], sorting)
  aggregate_csv_data(k, ['date', v, 'visits'], sorting)


# Aggregate the "top pages" reports
aggregateTopPages = {
  'all-pages-realtime.json': 'active_visitors',
  'top-pages-7-days.json': 'visits',
  'top-pages-30-days.json': 'visits'
}

for report in aggregateTopPages:
  with open(os.path.join(target_folder, report)) as json_file:
    data = json.load(json_file)
    value = aggregateTopPages[report]

    csv_file_writer(report, data['data'], ['domain', 'page', 'page_title', value], lambda x: -int(x[value]))


# Aggregate `users.csv`
with open(os.path.join(target_folder, 'users.json')) as json_file:
  data = json.load(json_file)
  csv_file_writer('users.json', data['data'], ['date', 'visits'], lambda x: x['date'])


# Copy all of the aggregated files into the final directory
src_files = os.listdir(target_folder)

for file_name in src_files:
    full_file_name = os.path.join(target_folder, file_name)

    if (os.path.isfile(full_file_name)):
        shutil.copy(full_file_name, report_folder)

# Delete the temporary folder
shutil.rmtree(target_folder)