---
frequency: realtime
meta:
  description: The top 20 pages, measured by active onsite users, for all sites.
  name: Top Pages (Live)
name: top-pages-realtime
query:
  dimensions:
  - rt:pagePath
  - rt:pageTitle
  max-results: '30'
  metrics:
  - rt:activeUsers
  sort: -rt:activeUsers
realtime: true

---