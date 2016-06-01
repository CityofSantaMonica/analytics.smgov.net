---
frequency: daily
meta:
  description: Data regarding each and every page
  name: All pages
name: all-pages
query:
  dimensions:
  - ga:date
  - ga:hostname
  - ga:pagePath
  - ga:pageTitle
  end-date: yesterday
  metrics:
  - ga:sessions
  - ga:percentNewSessions
  - ga:pageviews
  - ga:uniquePageviews
  - ga:avgTimeOnPage
  - ga:avgPageLoadTime
  - ga:entrances
  - ga:bounces
  - ga:exits
  start-date: yesterday

---
