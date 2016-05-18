---
frequency: daily
meta:
  description: 90 days of visits from Windows users, broken down by operating system
    version and date, for all sites.
  names: Windows
name: windows
query:
  dimensions:
  - ga:date
  - ga:operatingSystemVersion
  end-date: yesterday
  filters:
  - ga:operatingSystem==Windows
  metrics:
  - ga:sessions
  sort: ga:date
  start-date: 90daysAgo
slim: true

---