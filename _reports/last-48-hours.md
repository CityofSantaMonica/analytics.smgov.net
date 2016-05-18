---
frequency: realtime
meta:
  description: Today's visits for all sites.
  name: Today
name: last-48-hours
query:
  dimensions:
  - ga:date
  - ga:hour
  end-date: today
  metrics:
  - ga:sessions
  start-date: yesterday

---