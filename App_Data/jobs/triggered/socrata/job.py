#!/usr/bin/env python

import os
import sys

sitepackage = os.path.join(
    os.environ['HOME'], "site", "wwwroot",
    "pyenv", "lib", "python3.4", "site-packages"
)
sys.path.append(sitepackage)

import json
import re
from datetime import datetime, timedelta
from sodapy import Socrata

soda_client = Socrata(
    os.environ["SOCRATA_HOST"],
    os.environ["SOCRATA_APPTOKEN"],
    username=os.environ["SOCRATA_USER"],
    password=os.environ["SOCRATA_PASS"]
)
soda_batch_size = 950

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

def from_camel_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def clean_ga_keys(page):
    for key in page.keys():
        if key[:2] == 'ga':
            camel_key = from_camel_case(key[3:])
            page[camel_key] = page.pop(key)
    return page

percentages = [
    'percent_new_sessions',
    'avg_time_on_page',
    'avg_page_load_time',
    'bounce_rate',
    'entrance_rate',
    'exit_rate'
]

with open(os.path.join(report_folder, 'all-pages.json'), encoding='utf8') as json_file:
    data = json.load(json_file)
    taken_at = datetime.strptime(data['taken_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
    datestamp = (taken_at - timedelta(days=1)).strftime('%Y-%m-%d')

    for page in data['data']:
        page = clean_ga_keys(page)
        visits = int(page.pop('visits'))

        page['date'] = datestamp
        page['id'] = datestamp + page['domain'] + page['page']
        page['pageviews'] = visits

        if visits > 0:
            page['bounce_rate'] = 100 * float(page['bounces']) / visits
            page['entrance_rate'] = 100 * float(page['entrances']) / visits
            page['exit_rate'] = 100 * float(page['exits']) / visits

        for key in percentages:
            page[key] = round(float(page.get(key, 0)), 2)

    upsert_chunks = [ data['data'][x:x+soda_batch_size] for x in range(0, len(data['data']), soda_batch_size) ]

    for chunk in upsert_chunks:
        soda_client.upsert(os.environ["SOCRATA_RESOURCEID"], chunk)
