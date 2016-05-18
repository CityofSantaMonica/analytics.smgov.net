---
frequency: daily
meta:
  description: 90 days of desktop/mobile/tablet visits for all sites.
  name: Devices
name: devices
query:
  dimensions:
  - ga:date
  - ga:deviceCategory
  end-date: yesterday
  metrics:
  - ga:sessions
  sort: ga:date
  start-date: 90daysAgo
slim: true

---