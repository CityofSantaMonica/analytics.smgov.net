#!/usr/bin/env python

import csv
import json
import os
import shutil
import sys
from collections import Counter
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

def write_json_file(file_name, json_data):
    """
    Open `file_name` and dump JSON into the file
    """
    with open(os.path.join(target_folder, file_name), 'w', encoding='utf8') as data_file:
        json.dump(json_data, data_file, indent=4)

def json_file_writer(fileName, function):
    """
    Open `fileName` and load it as JSON. Call `function` and write the mutated `data` variable into the original file
    """
    with open(os.path.join(target_folder, fileName), 'r+', encoding='utf8') as data_file:
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

        if key not in output:
            output[key] = item
            output[key][sumKey] = int(output[key][sumKey])
        else:
            output[key][sumKey] += int(item[sumKey])

        if ignoreKeys is not None:
            for k in ignoreKeys:
                output[key].pop(k, None)

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

    with open(csvFile, 'w+', encoding='utf8') as csv_file:
        csvwriter = csv.DictWriter(csv_file, dialect='unix', fieldnames=fieldnames)
        csvwriter.writeheader()

        [ csvwriter.writerow(item) for item in sorted(data, key=sort) ]

def aggregate_csv_data(jsonFile, fieldnames, sort = None):

    with open(os.path.join(target_folder, jsonFile), encoding='utf8') as data_file:
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
    'top-pages-7-days.json': 'visits',
    'top-pages-30-days.json': 'visits',
    'top-pages-realtime.json': 'active_visitors'
}

# These keys need to be stripped from the respective reports
stripKeys = {
    'top-countries-realtime.json': ['domain'],
    'top-cities-realtime.json': ['domain']
}

# For certain reports, we'll have to borrow values from other reports in order to fix inconsistencies. This will method
# will make some not so smart assumptions and hopes it works.
borrowKeys = {
    "top-pages-7-days.json": ["domain"],
    "top-pages-30-days.json": ["domain"]
}

global_variables = {}
with open(os.path.join(os.environ['HOME'], "site", "wwwroot", "reports", "variables.json")) as data_file:
    global_variables = json.load(data_file)


# Aggregate all of the reports
# -----

for report in reports[2]:
    if not report.endswith('.json') or report in ignored_reports:
        continue

    jsonData = []

    for agency in agencies:
        reportFile = os.path.join(agency[0], report)

        try:
            with open(reportFile, encoding='utf8') as file_content:
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

                if report in borrowKeys:
                    c_agency = os.path.basename(agency[0])

                    for item in jsonData['data']:
                        if 'replace_done' not in item:
                            item['replace_done'] = False

                        for key_to_replace in borrowKeys[report]:
                            if not item['replace_done']:
                                item[key_to_replace] = global_variables[c_agency][key_to_replace]

                        item['replace_done'] = True

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

    if report in stripKeys or report in borrowKeys:
        for item in jsonData['data']:
            try:
                del item['replace_done']
                for key in stripKeys[report]:
                    del item[key]
            except KeyError:
                pass


    write_json_file(report, jsonData)


# Reports that need further, special, aggregation
# -----


# Let's count unique cities & countries and total up our active visitors and create the respective files
with open(os.path.join(target_folder, 'all-pages-realtime.json'), 'r+', encoding='utf8') as data_file:
    data = json.load(data_file)

    # City or country codes that should be ignored
    ignoreKeys = [ 'zz' ]

    # First tally up the number of entries for things, respectively
    countries = Counter([ k['country'] for k in data['data'] ])
    cities    = Counter([ k['city']    for k in data['data'] ])
    total     = sum([ int(k['active_visitors']) for k in data['data'] ])

    # Convert the tallies into dictionaries and sort them by visitors so our dashboard knows how to handle them
    countriesData = [ {'country': k[0], 'active_visitors': k[1]} for k in list(dict(countries).items()) if k[0] not in ignoreKeys ]
    countriesData = sorted(countriesData, key = lambda x: -x['active_visitors'])

    citiesData = [ {'city': k[0], 'active_visitors': k[1]} for k in list(dict(cities).items()) if k[0] not in ignoreKeys ]
    citiesData = sorted(citiesData, key = lambda x: -x['active_visitors'])

    # Write the data into the expected files so we don't have to break/change the dashboard
    write_json_file('top-countries-realtime.json', { 'data': countriesData })
    write_json_file('top-cities-realtime.json', { 'data': citiesData })
    write_json_file('realtime.json', { 'data': [{ 'active_visitors': total }] })


# Clean-up 'all-pages-realtime.json' from duplicate URLs and get rid of 'country' & 'city' keys while we're at it
sortCountKey = lambda x: -int(x[sumKey])
groupByKey = 'page'
ignoreKeys = [ 'country', 'city' ]
sumKey = 'active_visitors'
aggregate_list_sum_file('all-pages-realtime.json', groupByKey, sumKey, ignoreKeys, sortCountKey)


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
    with open(os.path.join(target_folder, report), encoding='utf8') as json_file:
        data = json.load(json_file)
        value = aggregateTopPages[report]

        csv_file_writer(report, data['data'], ['domain', 'page', 'page_title', value], lambda x: -int(x[value]))


# Aggregate `users.csv`
with open(os.path.join(target_folder, 'users.json'), encoding='utf8') as json_file:
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
