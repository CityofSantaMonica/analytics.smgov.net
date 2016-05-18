---
frequency: daily
meta:
  description: Last 30 days' top 20 pages, measured by page views, for all sites.
  name: Top Pages (30 Days)
name: top-pages-30-days
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
  start-date: 30daysAgo

---