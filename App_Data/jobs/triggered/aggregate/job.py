#!/usr/bin/env python

import csv
import json
import os
import shutil
import sys
from types import *
from random import shuffle
from collections import Counter

target_path = ''

def report_path(file_name):
    """
    Return the path to the location where aggregated data will be written to before it's deployed
    """
    return os.path.join(target_folder, file_name)

def csv_report_path(file_name):
    """
    Build a path to the target location for a CSV equivalent version from a JSON file name
    """
    csv_name = os.path.splitext(os.path.basename(file_name))[0] + '.csv'
    return report_path(csv_name)

def read_json_file(file_name):
    """
    Open `file_name` and parse it as JSON and return the respective content as a dictionary
    """
    with open(file_name, 'r', encoding='utf8') as data_file:
        return json.load(data_file)

def write_json_file(file_name, json_data):
    """
    Open `file_name` and dump JSON into the file; this function will overwrite everything that's in the file already
    """
    with open(file_name, 'w', encoding='utf8') as data_file:
        json.dump(json_data, data_file, indent=4)

def write_csv_file(file_name, data, headers):
    with open(file_name, 'w', encoding='utf8') as csv_file:
        csvwriter = csv.DictWriter(csv_file, dialect='unix', fieldnames=headers)
        csvwriter.writeheader()

        [ csvwriter.writerow(item) for item in data ]

def sum_shared_dict_keys(obj_one, obj_two):
    """
    Loop through all of the keys in a dictionary and find the sum for the respective values in both dictionaries. This
    function supports ints, lists, and dictionaries; anything else will be removed from the final result.

    See 'test_sum_shared_dict_keys' in test.py for sample usage and expected results
    """
    if not obj_one:
        return obj_two

    if not obj_two:
        return obj_one

    newObj = {}

    for key in obj_one:
        if isinstance(obj_one[key], (int, list)):
            newObj[key] = obj_one[key] + obj_two[key]
        elif isinstance(obj_one[key], dict):
            newObj[key] = sum_shared_dict_keys(obj_one[key], obj_two[key])

    return newObj

def sum_data_by_key(data, group_by, sum_key, keysToStrip = [], sort_by = None):
    """
    Sum up a specific key in an array of dictionaries. Each dictionary can be uniquely identified by the `group_by`,
    which can be a lambda or a string; use lambdas to concat two fields together to get a unique identifier for each
    dictionary.

    See 'test_sum_data_by_key' in test.py for sample usage and expected results
    """
    result = {}

    for entry in data:
        key = group_by(entry) if isinstance(group_by, LambdaType) else entry[group_by]

        if key not in result:
            result[key] = entry
            result[key][sum_key] = int(result[key][sum_key])
        else:
            result[key][sum_key] += int(entry[sum_key])

        for k in keysToStrip:
            result[key].pop(k, None)

    result = [ result[key] for key in result ]

    if sort_by is not None:
        result = sorted(result, key = sort_by)

    return result

def sum_data_by_key_file(file_name, group_by, sum_key, keys_to_strip, sort_by):
    with open(file_name, 'r+', encoding='utf8') as data_file:
        data = json.load(data_file)
        final_data = sum_data_by_key(data['data'], group_by, sum_key, keys_to_strip, sort_by)
        data['data'] = final_data[0:min(len(final_data), data['query']['max-results'])]

        data_file.seek(0)
        data_file.truncate()
        json.dump(data, data_file, indent=4)

        return data


if __name__ == "__main__":

    # Set some variables based on the environment we're in; i.e. production or development
    if len(sys.argv) > 1:
        cwd = '_site'
        report_folder = sys.argv[1]
    else:
        cwd = os.path.join(os.environ['HOME'], "site", "wwwroot")
        report_folder = os.path.join(cwd, os.environ["ANALYTICS_DATA_PATH"])

    # Where the aggregated data will go. We don't modify the data in place since it'll affect/break the website during
    # the process
    target_folder = report_folder + "_aggregation"

    # Make a temporary folder for data aggregation
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)

    os.mkdir(target_folder)

    # Reports that will not be aggregated by this script
    ignored_reports = []

    # Get all of our agencies and deleted the first item in the list. The first item is a collection of everything in
    # the folder and is safe to skip
    agencies = [ agency for agency in os.walk(report_folder) ]
    del agencies[0]

    # Get all of the reports for the smgov website. We will go on the assumption that the 'smgov' website will have all
    # of the reports
    reports = next(filter(lambda x: x[0] == "data/smgov", agencies))

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

    # Specific keys or fields that will be replaced during the aggregation based on the values retrieved from env.json
    findEnvReplace = {
        'all-pages-realtime.json': ['domain'],
        'top-pages-7-days.json': ['domain'],
        'top-pages-30-days.json': ['domain']
    }

    # Environment variables set during analytics fetching
    try:
        environment_vars = read_json_file(os.path.join(cwd, 'reports', 'env.json'))
    except FileNotFoundError:
        print("No environment variables have been defined. If you're in a dev environment, be sure to build the website first")
        exit()

    #
    # Aggregate all of the reports
    #

    # reports[2] is where all of the report file names are stored
    for report in reports[2]:
        if not report.endswith('.json') or report in ignored_reports:
            continue

        # ...short for 'aggregated'
        agg_data = []

        for agency in agencies:
            # agency[0] is the path to the agency
            report_file = os.path.join(agency[0], report)
            agency_name = os.path.basename(agency[0])

            try:
                with open(report_file, 'r+', encoding='utf8') as file_content:
                    data = json.load(file_content)

                    # Fields that need to be replaced based on environment variables due to Google Analytics returning
                    # data in a different format
                    try:
                        for key in findEnvReplace[report]:
                            for item in data['data']:
                                for env in environment_vars[agency_name]:
                                    item[key] = environment_vars[agency_name][env]

                        # Since we use data for individual websites now, we'll update individual website data with our
                        # replacements too
                        file_content.seek(0)
                        file_content.truncate()
                        json.dump(data, file_content, indent=4)
                    except KeyError:
                        pass

                    if not agg_data:
                        agg_data = data
                        continue

                    if 'data' in agg_data:
                        agg_data['data'] += data['data']

                    if 'totals' in agg_data:
                        agg_data['totals'] = sum_shared_dict_keys(agg_data['totals'], data['totals'])

            # This'll happen if the file was not found, meaning this agency isn't configured to have this report. For
            # example, not all websites will have the `realtime.json` report.
            except IOError:
                pass

        # If the report data requires to be sorted, sort the data for it based on the key specified. Any results that
        # match the value 1 will be shuffled so they are not listed alphabetically (there are a lot of these)
        if report in sortBy:
            sortKey = sortBy[report]
            sortedData = sorted(agg_data['data'], key=lambda x: -int(x[sortKey]))

            moreThanOneViewer = [item for item in sortedData if int(item[sortKey]) > 1]
            onlyOneViewer = [item for item in sortedData if int(item[sortKey]) == 1]

            shuffle(onlyOneViewer)
            sortedData = moreThanOneViewer + onlyOneViewer

            agg_data['data'] = sortedData[0:min(len(sortedData), agg_data['query']['max-results'])]

        if report in stripKeys:
            for item in agg_data['data']:
                for key in stripKeys[report]:
                    del item[key]

        write_json_file(report_path(report), agg_data)


    # Reports that need further, special, aggregation
    # -----


    # The 'all-pages-realtime.json' report contains data regarding active users based on cities and countries. In order
    # to avoid making a separate GA call, we'll tally up the number of users per city and country from this existing
    # report and create our own report that the dashboard will understand and accept
    with open(report_path('all-pages-realtime.json'), 'r+', encoding='utf8') as data_file:
        data = json.load(data_file)

        # City or country codes that should be ignored
        ignoreKeys = [ 'zz' ]

        # Tally up the number of entries for things, respectively. We'll receive a dictionary in the following format:
        #   {'United States': 50, 'Canada': 2}
        countries = Counter([ k['country'] for k in data['data'] ])
        cities    = Counter([ k['city']    for k in data['data'] ])
        total     = sum([ int(k['active_visitors']) for k in data['data'] ])

        # Convert the tallies into a list of dictionaries and sort them by visitors. By doing this, we'll be giving the
        # dashboard the syntax it expects
        countriesData = [ {'country': k[0], 'active_visitors': k[1]} for k in list(countries.items()) if k[0] not in ignoreKeys ]
        countriesData = sorted(countriesData, key = lambda x: -x['active_visitors'])
        citiesData = [ {'city': k[0], 'active_visitors': k[1]} for k in list(cities.items()) if k[0] not in ignoreKeys ]
        citiesData = sorted(citiesData, key = lambda x: -x['active_visitors'])

        # Write the data into the expected files so we don't have to break/change the dashboard
        write_json_file(report_path('top-countries-realtime.json'), { 'data': countriesData })
        write_json_file(report_path('top-cities-realtime.json'), { 'data': citiesData })
        write_json_file(report_path('realtime.json'), { 'data': [{ 'active_visitors': total }] })

    # Clean-up 'all-pages-realtime.json' from duplicate URLs and get rid of 'country' & 'city' keys while we're at it
    sortCountKey = lambda x: -int(x[sumKey])
    groupByKey = lambda x: x['domain'] + x['page']
    ignoreKeys = [ 'country', 'city' ]
    sumKey = 'active_visitors'
    sum_data_by_key_file(report_path('all-pages-realtime.json'), groupByKey, sumKey, ignoreKeys, sortCountKey)

    # Today.json aggregation
    sortCountKey = lambda x: int(x[groupByKey])
    groupByKey = 'hour'
    ignoreKeys = []
    sumKey = 'visits'
    sum_data_by_key_file(report_path('today.json'), groupByKey, sumKey, ignoreKeys, sortCountKey)
    sum_data_by_key_file(report_path('last-48-hours.json'), groupByKey, sumKey, ignoreKeys, sortCountKey)

    # Aggregate `users.json`
    sum_data_by_key_file(report_path('users.json'), 'date', 'visits', [], lambda x: x['date'])


    #
    # CSV Generation
    #


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
        file_name = report_path(k)

        data = sum_data_by_key_file(file_name, lambda x: x['date'] + x[v], 'visits', [], sorting)
        write_csv_file(csv_report_path(file_name), data['data'], ['date', v, 'visits'])

    # Aggregate the "top pages" reports
    aggregateTopPages = {
        'all-pages-realtime.json': 'active_visitors',
        'top-pages-7-days.json': 'visits',
        'top-pages-30-days.json': 'visits'
    }

    for report in aggregateTopPages:
        with open(report_path(report), encoding='utf8') as json_file:
            data = json.load(json_file)
            value = aggregateTopPages[report]

            write_csv_file(csv_report_path(report), data['data'], ['domain', 'page', 'page_title', value])

    # Aggregate `users.csv`
    with open(report_path('users.json'), encoding='utf8') as json_file:
        data = json.load(json_file)
        write_csv_file(csv_report_path('users.json'), data['data'], ['date', 'visits'])

    #
    # File moving and cleanup
    #

    # Copy all of the aggregated files into the final directory
    src_files = os.listdir(target_folder)

    for file_name in src_files:
        full_file_name = os.path.join(target_folder, file_name)

        if (os.path.isfile(full_file_name)):
            shutil.copy(full_file_name, report_folder)

    # Delete the temporary folder
    shutil.rmtree(target_folder)
