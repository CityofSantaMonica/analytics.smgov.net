---
frequency: daily
meta:
  description: User activity on specific pages.
  name: User Activity
name: user-activity
query:
  dimensions:
  - ga:date
  - ga:pagePath
  - ga:hostname
  - ga:pageTitle
  end-date: yesterday
  metrics:
  - ga:sessions
  - ga:bounceRate
  - ga:pageviews
  - ga:uniquePageviews
  - ga:avgTimeOnPage
  - ga:entrances
  - ga:entranceRate
  - ga:exits
  - ga:exitRate
  sort: ga:date
  start-date: yesterday

---