# Cal.com Upstream Outcomes

This file records upstream human response to Bayesilisk-generated findings.
It stores references and short summaries, not historical copies of full issue
threads.

## Public Unknown `rescheduleUid`

- Bayesilisk finding group:
  `calcom.unknown_reschedule_uid_must_not_open_booking_flow`
- Local result: public booking page with unknown/stale `rescheduleUid`
  returned semantic status `200`; expected `404`.
- Upstream issue: https://github.com/calcom/cal.diy/issues/29399
- Issue title: `Unknown rescheduleUid opens normal booking flow instead of 404`
- Issue state at capture: `open`
- Created by: `sashakolpakov`
- Created at: `2026-05-18T00:02:45Z`
- Human follow-up: contributor `nikhilgupta58` opened a fix PR and described
  the root cause as a missing null guard in `processReschedule`.
- Related Bayesilisk follow-up: the private booking-link `rescheduleUid`
  finding was added as a comment on the same issue thread before the fix PR.
- Fix PR: https://github.com/calcom/cal.diy/pull/29400
- Fix PR title:
  `fix: return 404 for unknown rescheduleUid instead of opening booking flow`
- Fix PR state at capture: `open`
- Fix PR created at: `2026-05-18T06:51:15Z`

Interpretation: this is evidence that the Bayesilisk finding was concrete
enough for a human contributor to produce a targeted fix.

## Cancelled Booking UID Replay

- Bayesilisk finding group:
  `calcom.cancelled_booking_uid_cannot_be_replayed_as_public_reschedule`
- Local result: generated workflow sequence
  `create-booking -> cancel-booking -> open-public-booking-route` returned
  semantic status `200`; expected `409`.
- Upstream issue: https://github.com/calcom/cal.diy/issues/29407
- Issue title:
  `Bayesilisk probe: cancelled booking UID replay opens public booking route`
- Issue state at capture: `open`
- Created by: `sashakolpakov`
- Created at: `2026-05-18T22:22:47Z`
- Bayesilisk attribution comment:
  https://github.com/calcom/cal.diy/issues/29407#issuecomment-4483000958

Interpretation: this issue is newly reported and has no upstream resolution at
capture time.
