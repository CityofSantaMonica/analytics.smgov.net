---
frequency: realtime
meta:
  description: Top countries for active onsite users.
  name: Top Cities
name: top-countries-realtime
query:
  dimensions:
  - rt:country
  metrics:
  - rt:activeUsers
  sort: -rt:activeUsers
realtime: true

---