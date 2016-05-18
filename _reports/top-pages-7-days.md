---
frequency: daily
meta:
  description: Last week's top 20 pages, measured by page views, for all sites.
  name: Top Pages (7 Days)
name: top-pages-7-days
query:
  dimensions:
  - ga:hostname
  - ga:pagePath
  - ga:pageTitle
  end-date: yesterday
  max-results: '30'
  metrics:
  - ga:pageviews
  sort: -ga:pageviews
  start-date: 7daysAgo

---