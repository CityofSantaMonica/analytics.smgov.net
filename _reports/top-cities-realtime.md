---
frequency: realtime
meta:
  description: Top cities for active onsite users.
  name: Top Cities (Live)
name: top-cities-realtime
query:
  dimensions:
  - rt:city
  metrics:
  - rt:activeUsers
  sort: -rt:activeUsers
realtime: true

---