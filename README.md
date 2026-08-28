# SupportDesk API

SupportDesk stores organization-scoped tickets and enforces a small status
state machine. Callers only see tickets belonging to their organization.

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m supportdesk.app
```

Trace `PATCH /tickets/{ticket_id}/status` through tenant lookup, transition
validation, immutable model replacement, persistence, and HTTP errors.

Design exercise: add SLA policies that escalate tickets based on priority and
business hours. Discuss policy storage, scheduled work, timezones, idempotency,
notifications, observability, and tests.

