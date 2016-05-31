#!/usr/bin/env python

import os
import sys

sitepackage = os.path.join(
  os.environ['HOME'], "site", "wwwroot",
  "pyenv", "lib", "python2.7", "site-packages"
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

percentages = [
  'avg_time_on_page',
  'bounce_rate',
  'entrance_rate',
  'exit_rate'
]

with open(os.path.join(report_folder, 'all-pages.json')) as json_file:
  data = json.load(json_file)
  taken_at = datetime.strptime(data['taken_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
  datestamp = (taken_at - timedelta(days=1)).strftime('%Y-%m-%d')

  for page in data['data']:
    page['date'] = datestamp
    page['id'] = datestamp + page['domain'] + page['page']

    for item in page.keys():
      if item == 'visits':
        page['pageviews'] = page.pop(item)

      if item[:2] == 'ga':
        key = from_camel_case(item[3:])
        page[key] = page.pop(item)

        if key in percentages:
          page[key] = round(float(page[key]), 2)

  soda_client.upsert(os.environ["SOCRATA_RESOURCEID"], data['data'])
