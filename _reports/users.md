---
frequency: daily
meta:
  description: 90 days of visits for all sites.
  name: Visitors
name: users
query:
  dimensions:
  - ga:date
  end-date: yesterday
  metrics:
  - ga:sessions
  sort: ga:date
  start-date: 90daysAgo
slim: true

---