---
frequency: daily
meta:
  description: 90 days of visits, broken down by operating system and date, for all
    sites.
  names: Operating Systems
name: os
query:
  dimensions:
  - ga:date
  - ga:operatingSystem
  end-date: yesterday
  metrics:
  - ga:sessions
  sort: ga:date
  start-date: 90daysAgo
slim: true

---