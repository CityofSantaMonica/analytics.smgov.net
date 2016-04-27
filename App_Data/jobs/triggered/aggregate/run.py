#!/usr/bin/env python

import json
import os
import sys

report_folder = 'data'
target_folder = report_folder

def merge_objects(objOne, objTwo):
    """
    Add keys from objTwo that do not exist in objOne to objOne
    """
    missingKeys = [ key for key in objTwo if key not in objOne ]

    for key in missingKeys:
        objOne[key] = objTwo[key]

def merge_add_objects(objOne, objTwo):
    """
    Merge two objects and add the respective values to get a total of both
    """
    for key in objOne:
        try:
            if isinstance(objOne[key], (int, list, tuple)):
                objOne[key] += objTwo[key]
            elif isinstance(objOne[key], dict):
                merge_add_objects(objOne[key], objTwo[key])
        except KeyError:
            pass

agencies = [ agency for agency in os.walk(report_folder) ] # Get all of our agencies
del agencies[0] # Delete the first entry, it has all of the folders and it's useless
reports = agencies[0] # Get all of the reports in the first agency's folder

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

                merge_objects(jsonData, data)

                try:
                    jsonData['data'] += data['data']
                except KeyError:
                    pass

                try:
                    merge_add_objects(jsonData['totals'], data['totals'])
                except KeyError:
                    pass

        except IOError:
            pass

    with open(os.path.join(target_folder, report), 'w+') as results_file:
        json.dump(jsonData, results_file)

# Reports that need further, special, aggregation
with open(os.path.join(target_folder, 'realtime.json'), 'w+') as data_file:
    data = json.load(data_file)
    active_visitors = 0

    for site in data['data']:
        active_visitors += int(site['active_visitors'])

    data['data'] = [{ "active_visitors": active_visitors }]

    data_file.seek(0)
    json.dump(data, data_file)
    data_file.truncate()