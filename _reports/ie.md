---
frequency: daily
meta:
  description: 90 days of visits from Internet Explorer users broken down by version
    for all sites.
  name: Internet Explorer
name: ie
query:
  dimensions:
  - ga:date
  - ga:browserVersion
  end-date: yesterday
  filters:
  - ga:browser==Internet Explorer
  metrics:
  - ga:sessions
  sort: ga:date,-ga:sessions
  start-date: 90daysAgo
slim: true

---