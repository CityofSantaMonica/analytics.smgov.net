---
frequency: daily
meta:
  description: Data regarding each and every page
  name: All pages
name: all-pages
query:
  dimensions:
  - ga:hostname
  - ga:pagePath
  - ga:pageTitle
  end-date: today
  metrics:
  - ga:entrances
  - ga:entranceRate
  - ga:pageviews
  - ga:uniquePageviews
  - ga:bounces
  - ga:bounceRate
  - ga:avgTimeOnPage
  - ga:exits
  - ga:exitRate
  start-date: yesterday

---