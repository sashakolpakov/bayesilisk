# Cal.com Bayesilisk Report

- App: Cal.com
- Repository: `https://github.com/calcom/cal.com`
- Tested commit: `180ede28f0bddf2738933a6e60a8e80f6116d7da`
- Seed: `150`
- Generated proposals: `7`
- Connector observations: `7`
- Verified app findings: `7`

## Findings

### Bayesilisk context-observed: Cancelled booking UID replay through public booking route is rejected

- Fingerprint: `bayesilisk:f6a7ea16be20efea`
- Invariant: `calcom.cancelled_booking_uid_cannot_be_replayed_as_public_reschedule`
- Classification: `breakage.context-observed`
- Expected: `409`
- Observed: `200`
- Route: `create-booking -> cancel-booking -> open-public-booking-route`
- Target URL: `http://localhost:3000/user-0-1779136802235/30-min`

### Bayesilisk context-observed: Dynamic booking page has a passing valid reschedule flow: stale id for rescheduleUid

- Fingerprint: `bayesilisk:0f97077a61e6fdea`
- Invariant: `calcom.dynamic_booking_unknown_reschedule_uid_must_not_open_booking_flow`
- Classification: `breakage.context-observed`
- Expected: `404`
- Observed: `200`
- Route: `/{username}+{username}?rescheduleUid={rescheduleUid}`
- Target URL: `http://localhost:3000/user-0-1779136720343+bayesilisk-dynamic-rWoI8w-0-1779136720580?rescheduleUid=stale-rescheduleUid`

### Bayesilisk context-observed: Dynamic booking page has a passing valid reschedule flow: unknown id for rescheduleUid

- Fingerprint: `bayesilisk:97a5026d569853f2`
- Invariant: `calcom.dynamic_booking_unknown_reschedule_uid_must_not_open_booking_flow`
- Classification: `breakage.context-observed`
- Expected: `404`
- Observed: `200`
- Route: `/{username}+{username}?rescheduleUid={rescheduleUid}`
- Target URL: `http://localhost:3000/user-0-1779136719738+bayesilisk-dynamic-ripWg2-0-1779136719983?rescheduleUid=missing-rescheduleUid`

### Bayesilisk context-observed: Private booking link resolves rescheduleUid into booking context: stale id for rescheduleUid

- Fingerprint: `bayesilisk:bfe8eaef0fc1701c`
- Invariant: `calcom.private_link_unknown_reschedule_uid_must_not_open_booking_flow`
- Classification: `breakage.context-observed`
- Expected: `404`
- Observed: `200`
- Route: `/d/{hashedLink}/{eventType}?rescheduleUid={rescheduleUid}`
- Target URL: `http://localhost:3000/d/9rh97aJE4zQmGhsbBcSXWF/30-min?rescheduleUid=stale-rescheduleUid`

### Bayesilisk context-observed: Private booking link resolves rescheduleUid into booking context: unknown id for rescheduleUid

- Fingerprint: `bayesilisk:024e5a53e41a7cf8`
- Invariant: `calcom.private_link_unknown_reschedule_uid_must_not_open_booking_flow`
- Classification: `breakage.context-observed`
- Expected: `404`
- Observed: `200`
- Route: `/d/{hashedLink}/{eventType}?rescheduleUid={rescheduleUid}`
- Target URL: `http://localhost:3000/d/23uVV2QM5FTEm1ZpGTMqAv/30-min?rescheduleUid=missing-rescheduleUid`

### Bayesilisk context-observed: TODO says missing rescheduleUid should force 404: stale id for rescheduleUid

- Fingerprint: `bayesilisk:b291afcc129f6e28`
- Invariant: `calcom.unknown_reschedule_uid_must_not_open_booking_flow`
- Classification: `breakage.context-observed`
- Expected: `404`
- Observed: `200`
- Route: `/{username}/{eventType}?rescheduleUid={rescheduleUid}&bookingUid=null`
- Target URL: `http://localhost:3000/user-0-1779136718407/30-min?rescheduleUid=stale-rescheduleUid&bookingUid=null`

### Bayesilisk context-observed: TODO says missing rescheduleUid should force 404: unknown id for rescheduleUid

- Fingerprint: `bayesilisk:b2a77c2dbcd3721a`
- Invariant: `calcom.unknown_reschedule_uid_must_not_open_booking_flow`
- Classification: `breakage.context-observed`
- Expected: `404`
- Observed: `200`
- Route: `/{username}/{eventType}?rescheduleUid={rescheduleUid}&bookingUid=null`
- Target URL: `http://localhost:3000/user-0-1779136716369/30-min?rescheduleUid=missing-rescheduleUid&bookingUid=null`
