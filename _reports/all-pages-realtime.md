---
frequency: realtime
meta:
  description: Pages, measured by active onsite users, for all sites.
  name: All Pages (Live)
name: all-pages-realtime
query:
  dimensions:
  - rt:pagePath
  - rt:pageTitle
  max-results: '10000'
  metrics:
  - rt:activeUsers
  sort: -rt:activeUsers
realtime: true
threshold:
  field: rt:activeUsers
  value: '1'

---