---
frequency: daily
meta:
  description: 90 days of visits broken down by browser for all sites.
  name: Browsers
name: browsers
query:
  dimensions:
  - ga:date
  - ga:browser
  end-date: yesterday
  metrics:
  - ga:sessions
  sort: ga:date,-ga:sessions
  start-date: 90daysAgo
slim: true

---