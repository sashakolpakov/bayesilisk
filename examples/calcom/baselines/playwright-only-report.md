# Bayesilisk Report

- Tool: `bayesilisk.v1.2`
- Seed: `150`
- Deterministic: `true`
- Production access: `false`
- Generated scenarios: `8`
- Grassmann attention: `grassmann-style-anchor-plane-proxy`
- Prioritization: Sort by posterior fault probability first. Fix or document breakage.easy findings, rerun with the same seed, then promote harder-to-find-after-easy-breakages modes.

## Sections

- Confirmed breakages: `46`
- Candidate probes: `2`
- Hard-to-find modes: `22`
- Controls: `51`

## Findings

### Bayesilisk context-observed: Private booking link must not ignore an unknown reschedule UID

- Scenario: `external.11` (context-observed)
- Fingerprint: `bayesilisk:595ca2c5e83cfd8c`
- Generated scenario: `false`
- Classification: `breakage.context-observed`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: External app invariant `calcom.private_link_unknown_reschedule_uid_must_not_open_booking_flow` must hold.
- Observed result: `fail`
- Observation: expected semantic status 404, observed 200 on `/d/{hashedLink}/{eventType}?rescheduleUid={unknownUid}`
- Observation basis: `confirmed-local-breakage`
- Attention score: `1.000000`
- Attention reasons: `connector-evidence, external-context-failure`
- Risk score: `0.990000`
- Sub-scenarios:
- Access pattern:
```json
{
  "actorRole": "attendee",
  "businessFlow": [],
  "dataSignals": {
    "expectedStatus": 404,
    "observedStatus": 200,
    "sourceContext": [
      "apps/web/lib/d/[link]/[slug]/getServerSideProps.tsx | Private booking link resolves rescheduleUid into booking context | Cal.com source signal: private booking link SSR validates the hashed link, then calls getBookingForReschedule when rescheduleUid is present before rendering booking props."
    ],
    "targetUrl": "http://localhost:3000/d/7PVRKUSmerk5WimZzh1E6X/30-min?rescheduleUid=missing-QgD9538yZUpI"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/d/{hashedLink}/{eventType}?rescheduleUid={unknownUid}"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `calcom.private_link_unknown_reschedule_uid_must_not_open_booking_flow`: Private booking link must not ignore an unknown reschedule UID.

Fingerprint: `bayesilisk:595ca2c5e83cfd8c`

Classification: `breakage.context-observed`

Issue readiness: `ready-for-issue`

Expected: semantic status `404`

Observed: semantic status `200`

Route: `/d/{hashedLink}/{eventType}?rescheduleUid={unknownUid}`

Target URL: `http://localhost:3000/d/7PVRKUSmerk5WimZzh1E6X/30-min?rescheduleUid=missing-QgD9538yZUpI`

Actor role: `attendee`

Source context:
- apps/web/lib/d/[link]/[slug]/getServerSideProps.tsx | Private booking link resolves rescheduleUid into booking context | Cal.com source signal: private booking link SSR validates the hashed link, then calls getBookingForReschedule when rescheduleUid is present before rendering booking props.

Evidence source: app-provided connector observation; Bayesilisk only compares deterministic observed facts.

Artifacts:

````

### Bayesilisk context-observed: Cancelled booking UID replay through public booking route is rejected

- Scenario: `external.5` (context-observed)
- Fingerprint: `bayesilisk:ca37bffc76216ad9`
- Generated scenario: `false`
- Classification: `breakage.context-observed`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: External app invariant `calcom.cancelled_booking_uid_cannot_be_replayed_as_public_reschedule` must hold.
- Observed result: `fail`
- Observation: expected semantic status 409, observed 200 on `/{username}/{eventType}?rescheduleUid={cancelledBookingUid}&bookingUid=null`
- Observation basis: `confirmed-local-breakage`
- Attention score: `1.000000`
- Attention reasons: `connector-evidence, external-context-failure`
- Risk score: `0.990000`
- Sub-scenarios:
- Access pattern:
```json
{
  "actorRole": "attendee",
  "businessFlow": [],
  "dataSignals": {
    "expectedStatus": 409,
    "observedStatus": 200,
    "sourceContext": [],
    "targetUrl": "http://localhost:3000/user-0-1779074296093/30-min"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/{username}/{eventType}?rescheduleUid={cancelledBookingUid}&bookingUid=null"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `calcom.cancelled_booking_uid_cannot_be_replayed_as_public_reschedule`: Cancelled booking UID replay through public booking route is rejected.

Fingerprint: `bayesilisk:ca37bffc76216ad9`

Classification: `breakage.context-observed`

Issue readiness: `ready-for-issue`

Expected: semantic status `409`

Observed: semantic status `200`

Route: `/{username}/{eventType}?rescheduleUid={cancelledBookingUid}&bookingUid=null`

Target URL: `http://localhost:3000/user-0-1779074296093/30-min`

Actor role: `attendee`

Source context:
- No repository source signal supplied.

Evidence source: app-provided connector observation; Bayesilisk only compares deterministic observed facts.

Artifacts:

````

### Bayesilisk context-observed: Unknown reschedule UID must not silently open the booking flow

- Scenario: `external.8` (context-observed)
- Fingerprint: `bayesilisk:6bd0a54ffc24461b`
- Generated scenario: `false`
- Classification: `breakage.context-observed`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: External app invariant `calcom.unknown_reschedule_uid_must_not_open_booking_flow` must hold.
- Observed result: `fail`
- Observation: expected semantic status 404, observed 200 on `/{username}/{eventType}?rescheduleUid={unknownUid}&bookingUid=null`
- Observation basis: `confirmed-local-breakage`
- Attention score: `1.000000`
- Attention reasons: `connector-evidence, external-context-failure`
- Risk score: `0.990000`
- Sub-scenarios:
- Access pattern:
```json
{
  "actorRole": "attendee",
  "businessFlow": [],
  "dataSignals": {
    "expectedStatus": 404,
    "observedStatus": 200,
    "sourceContext": [
      "apps/web/playwright/booking-seats.e2e.ts | TODO says missing rescheduleUid should force 404 | Cal.com source signal: booking-seats.e2e.ts contains `@TODO: force 404 when rescheduleUid is not found`; nearby tests exercise direct seated-event reschedule with `rescheduleUid` and `bookingUid=null`."
    ],
    "targetUrl": "http://localhost:3000/user-0-1779074299434/30-min?rescheduleUid=missing-buWDZod6ym74&bookingUid=null"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/{username}/{eventType}?rescheduleUid={unknownUid}&bookingUid=null"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `calcom.unknown_reschedule_uid_must_not_open_booking_flow`: Unknown reschedule UID must not silently open the booking flow.

Fingerprint: `bayesilisk:6bd0a54ffc24461b`

Classification: `breakage.context-observed`

Issue readiness: `ready-for-issue`

Expected: semantic status `404`

Observed: semantic status `200`

Route: `/{username}/{eventType}?rescheduleUid={unknownUid}&bookingUid=null`

Target URL: `http://localhost:3000/user-0-1779074299434/30-min?rescheduleUid=missing-buWDZod6ym74&bookingUid=null`

Actor role: `attendee`

Source context:
- apps/web/playwright/booking-seats.e2e.ts | TODO says missing rescheduleUid should force 404 | Cal.com source signal: booking-seats.e2e.ts contains `@TODO: force 404 when rescheduleUid is not found`; nearby tests exercise direct seated-event reschedule with `rescheduleUid` and `bookingUid=null`.

Evidence source: app-provided connector observation; Bayesilisk only compares deterministic observed facts.

Artifacts:

````

### Bayesilisk context-observed: Dynamic booking page must not ignore an unknown reschedule UID

- Scenario: `external.9` (context-observed)
- Fingerprint: `bayesilisk:5f909bdc2af05f9f`
- Generated scenario: `false`
- Classification: `breakage.context-observed`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: External app invariant `calcom.dynamic_booking_unknown_reschedule_uid_must_not_open_booking_flow` must hold.
- Observed result: `fail`
- Observation: expected semantic status 404, observed 200 on `/{username}+{username}?rescheduleUid={unknownUid}`
- Observation basis: `confirmed-local-breakage`
- Attention score: `1.000000`
- Attention reasons: `connector-evidence, external-context-failure`
- Risk score: `0.990000`
- Sub-scenarios:
- Access pattern:
```json
{
  "actorRole": "attendee",
  "businessFlow": [],
  "dataSignals": {
    "expectedStatus": 404,
    "observedStatus": 200,
    "sourceContext": [
      "apps/web/playwright/dynamic-booking-pages.e2e.ts | Dynamic booking page has a passing valid reschedule flow | Cal.com source signal: dynamic booking tests use rescheduleUid for a valid group booking reschedule; stale or unknown reschedule context should not silently become a new group booking."
    ],
    "targetUrl": "http://localhost:3000/user-0-1779074299848+bayesilisk-free-Yz77br-0-1779074300090?rescheduleUid=missing-Yu0oPJ4iTWpT"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/{username}+{username}?rescheduleUid={unknownUid}"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `calcom.dynamic_booking_unknown_reschedule_uid_must_not_open_booking_flow`: Dynamic booking page must not ignore an unknown reschedule UID.

Fingerprint: `bayesilisk:5f909bdc2af05f9f`

Classification: `breakage.context-observed`

Issue readiness: `ready-for-issue`

Expected: semantic status `404`

Observed: semantic status `200`

Route: `/{username}+{username}?rescheduleUid={unknownUid}`

Target URL: `http://localhost:3000/user-0-1779074299848+bayesilisk-free-Yz77br-0-1779074300090?rescheduleUid=missing-Yu0oPJ4iTWpT`

Actor role: `attendee`

Source context:
- apps/web/playwright/dynamic-booking-pages.e2e.ts | Dynamic booking page has a passing valid reschedule flow | Cal.com source signal: dynamic booking tests use rescheduleUid for a valid group booking reschedule; stale or unknown reschedule context should not silently become a new group booking.

Evidence source: app-provided connector observation; Bayesilisk only compares deterministic observed facts.

Artifacts:

````

### Bayesilisk breakage.hard-to-find: creative scenario violates roles.route_matrix_allowed

- Scenario: `creative.support_active_hr_document_shortcut` (creative)
- Fingerprint: `bayesilisk:9e8e7c6cb15e9c28`
- Generated scenario: `false`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `fail`
- Observation: role `support` is not allowed to access `/api/hr/documents`
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.969925`
- Sub-scenarios:
  - `role.support_takeover_active` [Support], complete alone: `false`
  - `hr.payroll_file_route` [HR], complete alone: `false`
  - `module.billing_on` [module entitlements], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `creative.support_active_hr_document_shortcut`: Active support takeover is still not a customer HR role for HR document download.

Fingerprint: `bayesilisk:9e8e7c6cb15e9c28`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: role `support` is not allowed to access `/api/hr/documents`

Risk score: 0.969925

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_active` (Support): Support actor has an active non-expired takeover session.
- `hr.payroll_file_route` (HR): HR document route is requested for another employee.
- `module.billing_on` (module entitlements): Billing module is enabled.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: creative scenario violates roles.route_matrix_allowed

- Scenario: `creative.support_foreign_dms_expense_review` (creative)
- Fingerprint: `bayesilisk:91da470436ae5da5`
- Generated scenario: `false`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `fail`
- Observation: role `support` is not allowed to access `/api/expense-claims/{claimId}/review`
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.969925`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `creative.support_foreign_dms_expense_review`: Expired support session tries to inspect a foreign DMS receipt during expense review.

Fingerprint: `bayesilisk:91da470436ae5da5`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: role `support` is not allowed to access `/api/expense-claims/{claimId}/review`

Risk score: 0.969925

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: generated-round-up scenario violates roles.route_matrix_allowed

- Scenario: `generated.05.employee_self.funding_approved.legs_consistent_multimodal` (generated-round-up)
- Fingerprint: `bayesilisk:f86335d563aa48c0`
- Generated scenario: `true`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `fail`
- Observation: role `employee` is not allowed to access `/api/travel/funding-requests/{requestId}/approve`
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.969925`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.05.employee_self.funding_approved.legs_consistent_multimodal`: Generated composite travel expense probe

Fingerprint: `bayesilisk:f86335d563aa48c0`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: role `employee` is not allowed to access `/api/travel/funding-requests/{requestId}/approve`

Risk score: 0.969925

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "employee",
    "businessFlow": [
      "travel funding request",
      "travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "targetEmployeeId": "emp-001",
      "transportModesCoveredByItinerary": true
    },
    "decision": "approve",
    "expenseCategories": [
      "rental_car",
      "train"
    ],
    "modules": {
      "expenses": false,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/travel/funding-requests/{requestId}/approve",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "rental_car",
      "train"
    ]
  },
  "fragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "route.travel_funding_approve",
    "travel.funding_approved",
    "route.expense_approve",
    "expense.rental_car",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.legs_consistent_multimodal",
    "creative.travel_expense_roundup"
  ],
  "observation": "role `employee` is not allowed to access `/api/travel/funding-requests/{requestId}/approve`"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "employee",
    "businessFlow": [],
    "dataSignals": {
      "targetEmployeeId": "emp-001"
    },
    "decision": "approve",
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/travel/funding-requests/{requestId}/approve"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.employee_self",
    "route.travel_funding_approve"
  ],
  "observation": "role `employee` is not allowed to access `/api/travel/funding-requests/{requestId}/approve`",
  "removedFragmentIds": [
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "travel.funding_approved",
    "route.expense_approve",
    "expense.rental_car",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.legs_consistent_multimodal",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved` (Travel): Travel funding is approved before expenses are submitted.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: generated-round-up scenario violates roles.route_matrix_allowed

- Scenario: `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:0dbb288b946886f3`
- Generated scenario: `true`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `fail`
- Observation: role `support` is not allowed to access `/api/travel/funding-requests`
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.969925`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:0dbb288b946886f3`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: role `support` is not allowed to access `/api/travel/funding-requests`

Risk score: 0.969925

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [
      "travel funding request",
      "late travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "transportModesCoveredByItinerary": false
    },
    "decision": "approve",
    "expenseCategories": [
      "airplane",
      "train"
    ],
    "modules": {
      "expenses": true,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "airplane",
      "train"
    ]
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.airfare",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ],
  "observation": "role `support` is not allowed to access `/api/travel/funding-requests`"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {},
    "decision": null,
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/travel/funding-requests"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "route.travel_funding_request"
  ],
  "observation": "role `support` is not allowed to access `/api/travel/funding-requests`",
  "removedFragmentIds": [
    "module.travel_on",
    "module.expenses_on",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.airfare",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: generated-round-up scenario violates roles.route_matrix_allowed

- Scenario: `generated.08.employee_self.funding_missing.mundane_itinerary` (generated-round-up)
- Fingerprint: `bayesilisk:6d83295f4b206d6f`
- Generated scenario: `true`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `fail`
- Observation: role `employee` is not allowed to access `/api/expense-claims/{claimId}/review`
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.969925`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_missing` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.08.employee_self.funding_missing.mundane_itinerary`: Generated composite travel expense probe

Fingerprint: `bayesilisk:6d83295f4b206d6f`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: role `employee` is not allowed to access `/api/expense-claims/{claimId}/review`

Risk score: 0.969925

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "employee",
    "businessFlow": [
      "travel funding request without approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "targetEmployeeId": "emp-001",
      "transportModesCoveredByItinerary": true
    },
    "decision": "approve",
    "expenseCategories": [
      "airplane",
      "train"
    ],
    "modules": {
      "expenses": false,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "airplane",
      "train"
    ]
  },
  "fragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "travel.funding_missing",
    "route.expense_approve",
    "expense.airfare",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.mundane_itinerary",
    "creative.travel_expense_roundup"
  ],
  "observation": "role `employee` is not allowed to access `/api/expense-claims/{claimId}/review`"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "employee",
    "businessFlow": [],
    "dataSignals": {
      "targetEmployeeId": "emp-001"
    },
    "decision": "approve",
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.employee_self",
    "route.expense_approve"
  ],
  "observation": "role `employee` is not allowed to access `/api/expense-claims/{claimId}/review`",
  "removedFragmentIds": [
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "travel.funding_missing",
    "expense.airfare",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.mundane_itinerary",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_missing` (Travel): Travel funding request exists but has no approval.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: generated-grassmann-attention scenario violates roles.route_matrix_allowed

- Scenario: `generated.attention.01.roles_route_matrix_allowed` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:766daf39831800eb`
- Generated scenario: `true`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `fail`
- Observation: role `support` is not allowed to access `/api/expense-claims/{claimId}/review`
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.969925`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.01.roles_route_matrix_allowed`: Grassmann-attention route matrix probe

Fingerprint: `bayesilisk:766daf39831800eb`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: role `support` is not allowed to access `/api/expense-claims/{claimId}/review`

Risk score: 0.969925

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {
      "allRequiredReceiptsUsable": false,
      "documentTenantMatches": false
    },
    "decision": "approve",
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "route.expense_approve",
    "expense.receipt_missing",
    "dms.foreign_tenant_document",
    "creative.travel_expense_roundup"
  ],
  "observation": "role `support` is not allowed to access `/api/expense-claims/{claimId}/review`"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {},
    "decision": "approve",
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "route.expense_approve"
  ],
  "observation": "role `support` is not allowed to access `/api/expense-claims/{claimId}/review`",
  "removedFragmentIds": [
    "expense.receipt_missing",
    "dms.foreign_tenant_document",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: generated-grassmann-attention scenario violates roles.route_matrix_allowed

- Scenario: `generated.attention.03.hr_documents_customer_role_boundary` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:45e8cf91b625e120`
- Generated scenario: `true`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `fail`
- Observation: role `support` is not allowed to access `/api/hr/documents`
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.969925`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `hr.payroll_file_route` [HR], complete alone: `false`
  - `module.billing_on` [module entitlements], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.03.hr_documents_customer_role_boundary`: Grassmann-attention HR document boundary probe

Fingerprint: `bayesilisk:45e8cf91b625e120`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: role `support` is not allowed to access `/api/hr/documents`

Risk score: 0.969925

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {
      "targetEmployeeId": "emp-002"
    },
    "decision": null,
    "expenseCategories": [],
    "modules": {
      "billing": true
    },
    "routes": [
      "/api/hr/documents"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "hr.payroll_file_route",
    "module.billing_on"
  ],
  "observation": "role `support` is not allowed to access `/api/hr/documents`"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {
      "targetEmployeeId": "emp-002"
    },
    "decision": null,
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/hr/documents"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "hr.payroll_file_route"
  ],
  "observation": "role `support` is not allowed to access `/api/hr/documents`",
  "removedFragmentIds": [
    "module.billing_on"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `hr.payroll_file_route` (HR): HR document route is requested for another employee.
- `module.billing_on` (module entitlements): Billing module is enabled.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: intentionally-inconsistent scenario violates roles.route_matrix_allowed

- Scenario: `inconsistent.employee_self_review_bad_itinerary` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:4dcfbbe26fd03b44`
- Generated scenario: `false`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `fail`
- Observation: role `employee` is not allowed to access `/api/expense-claims/{claimId}/review`
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.969925`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `travel.inconsistent_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.employee_self_review_bad_itinerary`: Employee self-approval is paired with an impossible itinerary.

Fingerprint: `bayesilisk:4dcfbbe26fd03b44`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: role `employee` is not allowed to access `/api/expense-claims/{claimId}/review`

Risk score: 0.969925

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `travel.inconsistent_itinerary` (Travel): Travel itinerary ends before it starts and contains non-chronological legs.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: round-up scenario violates roles.route_matrix_allowed

- Scenario: `roundup.support_hr_document_shortcut` (round-up)
- Fingerprint: `bayesilisk:05ff36361c4a2b16`
- Generated scenario: `false`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `fail`
- Observation: role `support` is not allowed to access `/api/hr/documents`
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.969925`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `hr.payroll_file_route` [HR], complete alone: `false`
  - `module.billing_on` [module entitlements], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `roundup.support_hr_document_shortcut`: Support-flavored HR document shortcut composed from partial actor and HR route fragments.

Fingerprint: `bayesilisk:05ff36361c4a2b16`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: role `support` is not allowed to access `/api/hr/documents`

Risk score: 0.969925

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `hr.payroll_file_route` (HR): HR document route is requested for another employee.
- `module.billing_on` (module entitlements): Billing module is enabled.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: creative scenario violates modules.expense_approval_requires_module_and_receipt

- Scenario: `creative.support_foreign_dms_expense_review` (creative)
- Fingerprint: `bayesilisk:e83da420e134ddd8`
- Generated scenario: `false`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `fail`
- Observation: expense approval reached while expenses module is disabled or absent
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.949640`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `creative.support_foreign_dms_expense_review`: Expired support session tries to inspect a foreign DMS receipt during expense review.

Fingerprint: `bayesilisk:e83da420e134ddd8`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval reached while expenses module is disabled or absent

Risk score: 0.949640

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-round-up scenario violates modules.expense_approval_requires_module_and_receipt

- Scenario: `generated.05.employee_self.funding_approved.legs_consistent_multimodal` (generated-round-up)
- Fingerprint: `bayesilisk:c8f7bc8b9b7042aa`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `fail`
- Observation: expense approval reached while expenses module is disabled or absent
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.949640`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.05.employee_self.funding_approved.legs_consistent_multimodal`: Generated composite travel expense probe

Fingerprint: `bayesilisk:c8f7bc8b9b7042aa`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval reached while expenses module is disabled or absent

Risk score: 0.949640

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "employee",
    "businessFlow": [
      "travel funding request",
      "travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "targetEmployeeId": "emp-001",
      "transportModesCoveredByItinerary": true
    },
    "decision": "approve",
    "expenseCategories": [
      "rental_car",
      "train"
    ],
    "modules": {
      "expenses": false,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/travel/funding-requests/{requestId}/approve",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "rental_car",
      "train"
    ]
  },
  "fragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "route.travel_funding_approve",
    "travel.funding_approved",
    "route.expense_approve",
    "expense.rental_car",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.legs_consistent_multimodal",
    "creative.travel_expense_roundup"
  ],
  "observation": "expense approval reached while expenses module is disabled or absent"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {},
    "decision": "approve",
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "route.expense_approve"
  ],
  "observation": "expense approval reached while expenses module is disabled or absent",
  "removedFragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "route.travel_funding_approve",
    "travel.funding_approved",
    "expense.rental_car",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.legs_consistent_multimodal",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved` (Travel): Travel funding is approved before expenses are submitted.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-round-up scenario violates modules.expense_approval_requires_module_and_receipt

- Scenario: `generated.08.employee_self.funding_missing.mundane_itinerary` (generated-round-up)
- Fingerprint: `bayesilisk:3c8912e3b0b2848f`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `fail`
- Observation: expense approval reached while expenses module is disabled or absent
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.949640`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_missing` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.08.employee_self.funding_missing.mundane_itinerary`: Generated composite travel expense probe

Fingerprint: `bayesilisk:3c8912e3b0b2848f`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval reached while expenses module is disabled or absent

Risk score: 0.949640

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "employee",
    "businessFlow": [
      "travel funding request without approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "targetEmployeeId": "emp-001",
      "transportModesCoveredByItinerary": true
    },
    "decision": "approve",
    "expenseCategories": [
      "airplane",
      "train"
    ],
    "modules": {
      "expenses": false,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "airplane",
      "train"
    ]
  },
  "fragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "travel.funding_missing",
    "route.expense_approve",
    "expense.airfare",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.mundane_itinerary",
    "creative.travel_expense_roundup"
  ],
  "observation": "expense approval reached while expenses module is disabled or absent"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {},
    "decision": "approve",
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "route.expense_approve"
  ],
  "observation": "expense approval reached while expenses module is disabled or absent",
  "removedFragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "travel.funding_missing",
    "expense.airfare",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.mundane_itinerary",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_missing` (Travel): Travel funding request exists but has no approval.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-grassmann-attention scenario violates modules.expense_approval_requires_module_and_receipt

- Scenario: `generated.attention.01.roles_route_matrix_allowed` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:2a792f796293de3e`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `fail`
- Observation: expense approval reached while expenses module is disabled or absent
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.949640`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.01.roles_route_matrix_allowed`: Grassmann-attention route matrix probe

Fingerprint: `bayesilisk:2a792f796293de3e`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval reached while expenses module is disabled or absent

Risk score: 0.949640

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {
      "allRequiredReceiptsUsable": false,
      "documentTenantMatches": false
    },
    "decision": "approve",
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "route.expense_approve",
    "expense.receipt_missing",
    "dms.foreign_tenant_document",
    "creative.travel_expense_roundup"
  ],
  "observation": "expense approval reached while expenses module is disabled or absent"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {},
    "decision": "approve",
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "route.expense_approve"
  ],
  "observation": "expense approval reached while expenses module is disabled or absent",
  "removedFragmentIds": [
    "role.support_takeover_expired",
    "expense.receipt_missing",
    "dms.foreign_tenant_document",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-grassmann-attention scenario violates modules.expense_approval_requires_module_and_receipt

- Scenario: `generated.attention.04.modules_expense_approval_requires_module_and_receipt` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:fabe7d2581800c30`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `fail`
- Observation: expense approval reached while expenses module is disabled or absent
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.949640`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.04.modules_expense_approval_requires_module_and_receipt`: Grassmann-attention disabled expense approval probe

Fingerprint: `bayesilisk:fabe7d2581800c30`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval reached while expenses module is disabled or absent

Risk score: 0.949640

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "finance",
    "businessFlow": [],
    "dataSignals": {
      "allRequiredReceiptsUsable": false,
      "documentTenantMatches": true
    },
    "decision": "approve",
    "expenseCategories": [],
    "modules": {
      "expenses": false
    },
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.finance",
    "module.expenses_off",
    "route.expense_approve",
    "expense.receipt_missing",
    "dms.correct_receipt",
    "creative.travel_expense_roundup"
  ],
  "observation": "expense approval reached while expenses module is disabled or absent"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {},
    "decision": "approve",
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "route.expense_approve"
  ],
  "observation": "expense approval reached while expenses module is disabled or absent",
  "removedFragmentIds": [
    "role.finance",
    "module.expenses_off",
    "expense.receipt_missing",
    "dms.correct_receipt",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: round-up scenario violates modules.expense_approval_requires_module_and_receipt

- Scenario: `roundup.expense_missing_receipt_disabled_module` (round-up)
- Fingerprint: `bayesilisk:06ba0de4162da124`
- Generated scenario: `false`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `fail`
- Observation: expense approval reached while expenses module is disabled or absent
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.949640`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `roundup.expense_missing_receipt_disabled_module`: Expense approval composed from disabled module, missing receipt, and travel context.

Fingerprint: `bayesilisk:06ba0de4162da124`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval reached while expenses module is disabled or absent

Risk score: 0.949640

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: creative scenario violates dms.tenant_process_boundary

- Scenario: `creative.support_foreign_dms_expense_review` (creative)
- Fingerprint: `bayesilisk:ea1acac5cb4c5c90`
- Generated scenario: `false`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `fail`
- Observation: DMS document crosses tenant boundary
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.906372`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `creative.support_foreign_dms_expense_review`: Expired support session tries to inspect a foreign DMS receipt during expense review.

Fingerprint: `bayesilisk:ea1acac5cb4c5c90`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document crosses tenant boundary

Risk score: 0.906372

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-round-up scenario violates dms.tenant_process_boundary

- Scenario: `generated.05.employee_self.funding_approved.legs_consistent_multimodal` (generated-round-up)
- Fingerprint: `bayesilisk:5e8746b4b976171a`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `fail`
- Observation: DMS document process `recruiting` does not match `travel_expense`
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.906372`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.05.employee_self.funding_approved.legs_consistent_multimodal`: Generated composite travel expense probe

Fingerprint: `bayesilisk:5e8746b4b976171a`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document process `recruiting` does not match `travel_expense`

Risk score: 0.906372

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "employee",
    "businessFlow": [
      "travel funding request",
      "travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "targetEmployeeId": "emp-001",
      "transportModesCoveredByItinerary": true
    },
    "decision": "approve",
    "expenseCategories": [
      "rental_car",
      "train"
    ],
    "modules": {
      "expenses": false,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/travel/funding-requests/{requestId}/approve",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "rental_car",
      "train"
    ]
  },
  "fragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "route.travel_funding_approve",
    "travel.funding_approved",
    "route.expense_approve",
    "expense.rental_car",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.legs_consistent_multimodal",
    "creative.travel_expense_roundup"
  ],
  "observation": "DMS document process `recruiting` does not match `travel_expense`"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {
      "documentTenantMatches": true
    },
    "decision": null,
    "expenseCategories": [],
    "modules": {},
    "routes": [],
    "transportModes": []
  },
  "fragmentIds": [
    "dms.wrong_process_document"
  ],
  "observation": "DMS document process `recruiting` does not match `travel_expense`",
  "removedFragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "route.travel_funding_approve",
    "travel.funding_approved",
    "route.expense_approve",
    "expense.rental_car",
    "expense.train_ticket",
    "travel.legs_consistent_multimodal",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved` (Travel): Travel funding is approved before expenses are submitted.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-round-up scenario violates dms.tenant_process_boundary

- Scenario: `generated.06.finance.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:0359033cf3302e65`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `fail`
- Observation: DMS document crosses tenant boundary
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.906372`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.06.finance.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:0359033cf3302e65`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document crosses tenant boundary

Risk score: 0.906372

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "finance",
    "businessFlow": [
      "travel funding request",
      "late travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": false,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "transportModesCoveredByItinerary": false
    },
    "decision": "approve",
    "expenseCategories": [
      "rental_car",
      "train"
    ],
    "modules": {
      "expenses": true,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "rental_car",
      "train"
    ]
  },
  "fragmentIds": [
    "role.finance",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.rental_car",
    "expense.train_ticket",
    "dms.foreign_tenant_document",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ],
  "observation": "DMS document crosses tenant boundary"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {
      "documentTenantMatches": false
    },
    "decision": null,
    "expenseCategories": [],
    "modules": {},
    "routes": [],
    "transportModes": []
  },
  "fragmentIds": [
    "dms.foreign_tenant_document"
  ],
  "observation": "DMS document crosses tenant boundary",
  "removedFragmentIds": [
    "role.finance",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.rental_car",
    "expense.train_ticket",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-round-up scenario violates dms.tenant_process_boundary

- Scenario: `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:27575720e82f299c`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `fail`
- Observation: DMS document process `recruiting` does not match `travel_expense`
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.906372`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:27575720e82f299c`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document process `recruiting` does not match `travel_expense`

Risk score: 0.906372

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [
      "travel funding request",
      "late travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "transportModesCoveredByItinerary": false
    },
    "decision": "approve",
    "expenseCategories": [
      "airplane",
      "train"
    ],
    "modules": {
      "expenses": true,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "airplane",
      "train"
    ]
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.airfare",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ],
  "observation": "DMS document process `recruiting` does not match `travel_expense`"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {
      "documentTenantMatches": true
    },
    "decision": null,
    "expenseCategories": [],
    "modules": {},
    "routes": [],
    "transportModes": []
  },
  "fragmentIds": [
    "dms.wrong_process_document"
  ],
  "observation": "DMS document process `recruiting` does not match `travel_expense`",
  "removedFragmentIds": [
    "role.support_takeover_expired",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.airfare",
    "expense.train_ticket",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-round-up scenario violates dms.tenant_process_boundary

- Scenario: `generated.08.employee_self.funding_missing.mundane_itinerary` (generated-round-up)
- Fingerprint: `bayesilisk:cc953a347e4d60c9`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `fail`
- Observation: DMS document process `recruiting` does not match `travel_expense`
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.906372`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_missing` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.08.employee_self.funding_missing.mundane_itinerary`: Generated composite travel expense probe

Fingerprint: `bayesilisk:cc953a347e4d60c9`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document process `recruiting` does not match `travel_expense`

Risk score: 0.906372

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "employee",
    "businessFlow": [
      "travel funding request without approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "targetEmployeeId": "emp-001",
      "transportModesCoveredByItinerary": true
    },
    "decision": "approve",
    "expenseCategories": [
      "airplane",
      "train"
    ],
    "modules": {
      "expenses": false,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "airplane",
      "train"
    ]
  },
  "fragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "travel.funding_missing",
    "route.expense_approve",
    "expense.airfare",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.mundane_itinerary",
    "creative.travel_expense_roundup"
  ],
  "observation": "DMS document process `recruiting` does not match `travel_expense`"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {
      "documentTenantMatches": true
    },
    "decision": null,
    "expenseCategories": [],
    "modules": {},
    "routes": [],
    "transportModes": []
  },
  "fragmentIds": [
    "dms.wrong_process_document"
  ],
  "observation": "DMS document process `recruiting` does not match `travel_expense`",
  "removedFragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "travel.funding_missing",
    "route.expense_approve",
    "expense.airfare",
    "expense.train_ticket",
    "travel.mundane_itinerary",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_missing` (Travel): Travel funding request exists but has no approval.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-grassmann-attention scenario violates dms.tenant_process_boundary

- Scenario: `generated.attention.01.roles_route_matrix_allowed` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:3f3e37bdd14c4cd8`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `fail`
- Observation: DMS document crosses tenant boundary
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.906372`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.01.roles_route_matrix_allowed`: Grassmann-attention route matrix probe

Fingerprint: `bayesilisk:3f3e37bdd14c4cd8`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document crosses tenant boundary

Risk score: 0.906372

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {
      "allRequiredReceiptsUsable": false,
      "documentTenantMatches": false
    },
    "decision": "approve",
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "route.expense_approve",
    "expense.receipt_missing",
    "dms.foreign_tenant_document",
    "creative.travel_expense_roundup"
  ],
  "observation": "DMS document crosses tenant boundary"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {
      "documentTenantMatches": false
    },
    "decision": null,
    "expenseCategories": [],
    "modules": {},
    "routes": [],
    "transportModes": []
  },
  "fragmentIds": [
    "dms.foreign_tenant_document"
  ],
  "observation": "DMS document crosses tenant boundary",
  "removedFragmentIds": [
    "role.support_takeover_expired",
    "route.expense_approve",
    "expense.receipt_missing",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-grassmann-attention scenario violates dms.tenant_process_boundary

- Scenario: `generated.attention.02.dms_tenant_process_boundary` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:60b8e58a539825d1`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `fail`
- Observation: DMS document crosses tenant boundary
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.906372`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.02.dms_tenant_process_boundary`: Grassmann-attention foreign DMS evidence probe

Fingerprint: `bayesilisk:60b8e58a539825d1`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document crosses tenant boundary

Risk score: 0.906372

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "finance",
    "businessFlow": [],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": false,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "transportModesCoveredByItinerary": true
    },
    "decision": "approve",
    "expenseCategories": [
      "rental_car"
    ],
    "modules": {
      "expenses": true
    },
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "rental_car"
    ]
  },
  "fragmentIds": [
    "role.finance",
    "module.expenses_on",
    "route.expense_approve",
    "expense.rental_car",
    "dms.foreign_tenant_document",
    "travel.mundane_itinerary"
  ],
  "observation": "DMS document crosses tenant boundary"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {
      "documentTenantMatches": false
    },
    "decision": null,
    "expenseCategories": [],
    "modules": {},
    "routes": [],
    "transportModes": []
  },
  "fragmentIds": [
    "dms.foreign_tenant_document"
  ],
  "observation": "DMS document crosses tenant boundary",
  "removedFragmentIds": [
    "role.finance",
    "module.expenses_on",
    "route.expense_approve",
    "expense.rental_car",
    "travel.mundane_itinerary"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: intentionally-inconsistent scenario violates dms.tenant_process_boundary

- Scenario: `inconsistent.dms_wrong_process_receipt` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:6e8a16fa90e5cbd6`
- Generated scenario: `false`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `fail`
- Observation: DMS document process `recruiting` does not match `travel_expense`
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.906372`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.dms_wrong_process_receipt`: Tenant-scoped DMS evidence comes from the recruiting process during travel expense review.

Fingerprint: `bayesilisk:6e8a16fa90e5cbd6`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document process `recruiting` does not match `travel_expense`

Risk score: 0.906372

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: intentionally-inconsistent scenario violates roles.employee_self_review_forbidden

- Scenario: `inconsistent.employee_self_review_bad_itinerary` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:9ed756c3582a4ebb`
- Generated scenario: `false`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `highest-fault-probability`
- Expected invariant: Employee self-review remains forbidden for approvals.
- Observed result: `fail`
- Observation: employee self-review would approve their own record
- Observation basis: `fresh-prior`
- Attention score: `0.373000`
- Attention reasons: `untested-plane`
- Risk score: `0.895461`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `travel.inconsistent_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.employee_self_review_bad_itinerary`: Employee self-approval is paired with an impossible itinerary.

Fingerprint: `bayesilisk:9ed756c3582a4ebb`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `highest-fault-probability`

Expected invariant: Employee self-review remains forbidden for approvals.

Observed: employee self-review would approve their own record

Risk score: 0.895461

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `travel.inconsistent_itinerary` (Travel): Travel itinerary ends before it starts and contains non-chronological legs.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: creative scenario violates support.takeover_session_required

- Scenario: `creative.support_foreign_dms_expense_review` (creative)
- Fingerprint: `bayesilisk:67268fb65d9d57b6`
- Generated scenario: `false`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `fault-probability-elevated`
- Expected invariant: Support access requires active non-expired takeover scope.
- Observed result: `fail`
- Observation: support access lacks an active non-expired takeover session
- Observation basis: `fresh-prior`
- Attention score: `0.376000`
- Attention reasons: `untested-plane`
- Risk score: `0.846715`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `creative.support_foreign_dms_expense_review`: Expired support session tries to inspect a foreign DMS receipt during expense review.

Fingerprint: `bayesilisk:67268fb65d9d57b6`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `fault-probability-elevated`

Expected invariant: Support access requires active non-expired takeover scope.

Observed: support access lacks an active non-expired takeover session

Risk score: 0.846715

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-grassmann-attention scenario violates support.takeover_session_required

- Scenario: `generated.attention.01.roles_route_matrix_allowed` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:bf9294b72c509fc0`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `fault-probability-elevated`
- Expected invariant: Support access requires active non-expired takeover scope.
- Observed result: `fail`
- Observation: support access lacks an active non-expired takeover session
- Observation basis: `fresh-prior`
- Attention score: `0.376000`
- Attention reasons: `untested-plane`
- Risk score: `0.846715`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.01.roles_route_matrix_allowed`: Grassmann-attention route matrix probe

Fingerprint: `bayesilisk:bf9294b72c509fc0`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `fault-probability-elevated`

Expected invariant: Support access requires active non-expired takeover scope.

Observed: support access lacks an active non-expired takeover session

Risk score: 0.846715

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": false
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {
      "allRequiredReceiptsUsable": false,
      "documentTenantMatches": false
    },
    "decision": "approve",
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "route.expense_approve",
    "expense.receipt_missing",
    "dms.foreign_tenant_document",
    "creative.travel_expense_roundup"
  ],
  "observation": "support access lacks an active non-expired takeover session"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {},
    "decision": null,
    "expenseCategories": [],
    "modules": {},
    "routes": [],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired"
  ],
  "observation": "support access lacks an active non-expired takeover session",
  "removedFragmentIds": [
    "route.expense_approve",
    "expense.receipt_missing",
    "dms.foreign_tenant_document",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: generated-grassmann-attention scenario violates support.takeover_session_required

- Scenario: `generated.attention.03.hr_documents_customer_role_boundary` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:db9bf72061a22078`
- Generated scenario: `true`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `fault-probability-elevated`
- Expected invariant: Support access requires active non-expired takeover scope.
- Observed result: `fail`
- Observation: support access lacks an active non-expired takeover session
- Observation basis: `fresh-prior`
- Attention score: `0.376000`
- Attention reasons: `untested-plane`
- Risk score: `0.846715`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `hr.payroll_file_route` [HR], complete alone: `false`
  - `module.billing_on` [module entitlements], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.03.hr_documents_customer_role_boundary`: Grassmann-attention HR document boundary probe

Fingerprint: `bayesilisk:db9bf72061a22078`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `fault-probability-elevated`

Expected invariant: Support access requires active non-expired takeover scope.

Observed: support access lacks an active non-expired takeover session

Risk score: 0.846715

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {
      "targetEmployeeId": "emp-002"
    },
    "decision": null,
    "expenseCategories": [],
    "modules": {
      "billing": true
    },
    "routes": [
      "/api/hr/documents"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "hr.payroll_file_route",
    "module.billing_on"
  ],
  "observation": "support access lacks an active non-expired takeover session"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {},
    "decision": null,
    "expenseCategories": [],
    "modules": {},
    "routes": [],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired"
  ],
  "observation": "support access lacks an active non-expired takeover session",
  "removedFragmentIds": [
    "hr.payroll_file_route",
    "module.billing_on"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `hr.payroll_file_route` (HR): HR document route is requested for another employee.
- `module.billing_on` (module entitlements): Billing module is enabled.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: round-up scenario violates support.takeover_session_required

- Scenario: `roundup.support_hr_document_shortcut` (round-up)
- Fingerprint: `bayesilisk:952185e936d42291`
- Generated scenario: `false`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `fault-probability-elevated`
- Expected invariant: Support access requires active non-expired takeover scope.
- Observed result: `fail`
- Observation: support access lacks an active non-expired takeover session
- Observation basis: `fresh-prior`
- Attention score: `0.376000`
- Attention reasons: `untested-plane`
- Risk score: `0.846715`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `hr.payroll_file_route` [HR], complete alone: `false`
  - `module.billing_on` [module entitlements], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `roundup.support_hr_document_shortcut`: Support-flavored HR document shortcut composed from partial actor and HR route fragments.

Fingerprint: `bayesilisk:952185e936d42291`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `fault-probability-elevated`

Expected invariant: Support access requires active non-expired takeover scope.

Observed: support access lacks an active non-expired takeover session

Risk score: 0.846715

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `hr.payroll_file_route` (HR): HR document route is requested for another employee.
- `module.billing_on` (module entitlements): Billing module is enabled.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.easy: round-up scenario violates billing.export_requires_role_and_module

- Scenario: `roundup.billing_export_disabled_module` (round-up)
- Fingerprint: `bayesilisk:7d247d67deddf23a`
- Generated scenario: `false`
- Classification: `breakage.easy`
- Issue readiness: `ready-for-issue`
- Posterior mode: `fault-probability-elevated`
- Expected invariant: Billing exports require billing entitlement and finance/admin role.
- Observed result: `fail`
- Observation: billing export requested without billing module entitlement
- Observation basis: `fresh-prior`
- Attention score: `0.361000`
- Attention reasons: `untested-plane`
- Risk score: `0.812500`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.billing_off` [module entitlements], complete alone: `false`
  - `billing.export_route` [Billing], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": false
  },
  "routes": [
    "/api/billing/exports"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `roundup.billing_export_disabled_module`: Finance actor reaches billing export while the billing module is disabled.

Fingerprint: `bayesilisk:7d247d67deddf23a`

Classification: `breakage.easy`

Issue readiness: `ready-for-issue`

Posterior mode: `fault-probability-elevated`

Expected invariant: Billing exports require billing entitlement and finance/admin role.

Observed: billing export requested without billing module entitlement

Risk score: 0.812500

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": false
  },
  "routes": [
    "/api/billing/exports"
  ],
  "transportModes": []
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.billing_off` (module entitlements): Billing module is disabled.
- `billing.export_route` (Billing): Billing export route is requested.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: generated-round-up scenario violates travel.funding_before_expense

- Scenario: `generated.06.finance.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:e188a5fcf8b87e88`
- Generated scenario: `true`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: Travel expenses require approved funding before expense submission or approval.
- Observed result: `fail`
- Observation: travel expense was submitted before funding approval
- Observation basis: `invariant-adjustment:travel.funding_before_expense`
- Attention score: `0.354333`
- Attention reasons: `untested-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.801700`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.06.finance.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:e188a5fcf8b87e88`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: Travel expenses require approved funding before expense submission or approval.

Observed: travel expense was submitted before funding approval

Risk score: 0.801700

Observation basis:
```json
{
  "priorDelta": 0.018,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:travel.funding_before_expense"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "finance",
    "businessFlow": [
      "travel funding request",
      "late travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": false,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "transportModesCoveredByItinerary": false
    },
    "decision": "approve",
    "expenseCategories": [
      "rental_car",
      "train"
    ],
    "modules": {
      "expenses": true,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "rental_car",
      "train"
    ]
  },
  "fragmentIds": [
    "role.finance",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.rental_car",
    "expense.train_ticket",
    "dms.foreign_tenant_document",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ],
  "observation": "travel expense was submitted before funding approval"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [
      "travel funding request",
      "late travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true
    },
    "decision": null,
    "expenseCategories": [
      "train"
    ],
    "modules": {},
    "routes": [],
    "transportModes": [
      "train"
    ]
  },
  "fragmentIds": [
    "travel.funding_approved_late",
    "expense.train_ticket"
  ],
  "observation": "travel expense was submitted before funding approval",
  "removedFragmentIds": [
    "role.finance",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "route.expense_approve",
    "expense.rental_car",
    "dms.foreign_tenant_document",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: generated-round-up scenario violates travel.funding_before_expense

- Scenario: `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:7f3fc31f4e964089`
- Generated scenario: `true`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: Travel expenses require approved funding before expense submission or approval.
- Observed result: `fail`
- Observation: travel expense was submitted before funding approval
- Observation basis: `invariant-adjustment:travel.funding_before_expense`
- Attention score: `0.354333`
- Attention reasons: `untested-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.801700`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:7f3fc31f4e964089`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: Travel expenses require approved funding before expense submission or approval.

Observed: travel expense was submitted before funding approval

Risk score: 0.801700

Observation basis:
```json
{
  "priorDelta": 0.018,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:travel.funding_before_expense"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [
      "travel funding request",
      "late travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "transportModesCoveredByItinerary": false
    },
    "decision": "approve",
    "expenseCategories": [
      "airplane",
      "train"
    ],
    "modules": {
      "expenses": true,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "airplane",
      "train"
    ]
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.airfare",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ],
  "observation": "travel expense was submitted before funding approval"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [
      "travel funding request",
      "late travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true
    },
    "decision": null,
    "expenseCategories": [
      "train"
    ],
    "modules": {},
    "routes": [],
    "transportModes": [
      "train"
    ]
  },
  "fragmentIds": [
    "travel.funding_approved_late",
    "expense.train_ticket"
  ],
  "observation": "travel expense was submitted before funding approval",
  "removedFragmentIds": [
    "role.support_takeover_expired",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "route.expense_approve",
    "expense.airfare",
    "dms.wrong_process_document",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: generated-round-up scenario violates travel.funding_before_expense

- Scenario: `generated.08.employee_self.funding_missing.mundane_itinerary` (generated-round-up)
- Fingerprint: `bayesilisk:580bfd4737078a96`
- Generated scenario: `true`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: Travel expenses require approved funding before expense submission or approval.
- Observed result: `fail`
- Observation: travel expense flow has a funding request but no approved funding
- Observation basis: `invariant-adjustment:travel.funding_before_expense`
- Attention score: `0.354333`
- Attention reasons: `untested-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.801700`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_missing` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.08.employee_self.funding_missing.mundane_itinerary`: Generated composite travel expense probe

Fingerprint: `bayesilisk:580bfd4737078a96`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: Travel expenses require approved funding before expense submission or approval.

Observed: travel expense flow has a funding request but no approved funding

Risk score: 0.801700

Observation basis:
```json
{
  "priorDelta": 0.018,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:travel.funding_before_expense"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "employee",
    "businessFlow": [
      "travel funding request without approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "targetEmployeeId": "emp-001",
      "transportModesCoveredByItinerary": true
    },
    "decision": "approve",
    "expenseCategories": [
      "airplane",
      "train"
    ],
    "modules": {
      "expenses": false,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "airplane",
      "train"
    ]
  },
  "fragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "route.travel_funding_request",
    "travel.funding_missing",
    "route.expense_approve",
    "expense.airfare",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.mundane_itinerary",
    "creative.travel_expense_roundup"
  ],
  "observation": "travel expense flow has a funding request but no approved funding"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {
      "allRequiredReceiptsUsable": true
    },
    "decision": null,
    "expenseCategories": [
      "train"
    ],
    "modules": {},
    "routes": [
      "/api/travel/funding-requests"
    ],
    "transportModes": [
      "train"
    ]
  },
  "fragmentIds": [
    "route.travel_funding_request",
    "expense.train_ticket"
  ],
  "observation": "travel expense flow has a funding request but no approved funding",
  "removedFragmentIds": [
    "role.employee_self",
    "module.travel_on",
    "module.expenses_off",
    "travel.funding_missing",
    "route.expense_approve",
    "expense.airfare",
    "dms.wrong_process_document",
    "travel.mundane_itinerary",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_missing` (Travel): Travel funding request exists but has no approval.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: round-up scenario violates travel.funding_before_expense

- Scenario: `roundup.travel_expense_before_late_funding` (round-up)
- Fingerprint: `bayesilisk:7129b46737caea36`
- Generated scenario: `false`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: Travel expenses require approved funding before expense submission or approval.
- Observed result: `fail`
- Observation: travel expense was submitted before funding approval
- Observation basis: `invariant-adjustment:travel.funding_before_expense`
- Attention score: `0.354333`
- Attention reasons: `untested-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.801700`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `roundup.travel_expense_before_late_funding`: Travel expense is submitted before a late funding approval lands.

Fingerprint: `bayesilisk:7129b46737caea36`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: Travel expenses require approved funding before expense submission or approval.

Observed: travel expense was submitted before funding approval

Risk score: 0.801700

Observation basis:
```json
{
  "priorDelta": 0.018,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:travel.funding_before_expense"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: round-up scenario violates travel.funding_before_expense

- Scenario: `roundup.travel_funding_unapproved_multimodal_expense` (round-up)
- Fingerprint: `bayesilisk:5d61b19946e00d5d`
- Generated scenario: `false`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: Travel expenses require approved funding before expense submission or approval.
- Observed result: `fail`
- Observation: travel expense flow has a funding request but no approved funding
- Observation basis: `invariant-adjustment:travel.funding_before_expense`
- Attention score: `0.354333`
- Attention reasons: `untested-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.801700`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_missing` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `roundup.travel_funding_unapproved_multimodal_expense`: Rental car, train, and airplane expenses are approved after a funding request with no approval.

Fingerprint: `bayesilisk:5d61b19946e00d5d`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: Travel expenses require approved funding before expense submission or approval.

Observed: travel expense flow has a funding request but no approved funding

Risk score: 0.801700

Observation basis:
```json
{
  "priorDelta": 0.018,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:travel.funding_before_expense"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_missing` (Travel): Travel funding request exists but has no approval.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: creative scenario violates hr.documents_customer_role_boundary

- Scenario: `creative.support_active_hr_document_shortcut` (creative)
- Fingerprint: `bayesilisk:c751cd907410c74f`
- Generated scenario: `false`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: HR document routes require customer HR/admin roles, not support/platform shortcuts.
- Observed result: `fail`
- Observation: HR document action requires HR/admin/customer owner role
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.774295`
- Sub-scenarios:
  - `role.support_takeover_active` [Support], complete alone: `false`
  - `hr.payroll_file_route` [HR], complete alone: `false`
  - `module.billing_on` [module entitlements], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `creative.support_active_hr_document_shortcut`: Active support takeover is still not a customer HR role for HR document download.

Fingerprint: `bayesilisk:c751cd907410c74f`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: HR document routes require customer HR/admin roles, not support/platform shortcuts.

Observed: HR document action requires HR/admin/customer owner role

Risk score: 0.774295

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_active` (Support): Support actor has an active non-expired takeover session.
- `hr.payroll_file_route` (HR): HR document route is requested for another employee.
- `module.billing_on` (module entitlements): Billing module is enabled.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: generated-grassmann-attention scenario violates hr.documents_customer_role_boundary

- Scenario: `generated.attention.03.hr_documents_customer_role_boundary` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:32754fa404b50f26`
- Generated scenario: `true`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: HR document routes require customer HR/admin roles, not support/platform shortcuts.
- Observed result: `fail`
- Observation: HR document action requires HR/admin/customer owner role
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.774295`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `hr.payroll_file_route` [HR], complete alone: `false`
  - `module.billing_on` [module entitlements], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.03.hr_documents_customer_role_boundary`: Grassmann-attention HR document boundary probe

Fingerprint: `bayesilisk:32754fa404b50f26`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: HR document routes require customer HR/admin roles, not support/platform shortcuts.

Observed: HR document action requires HR/admin/customer owner role

Risk score: 0.774295

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {
      "targetEmployeeId": "emp-002"
    },
    "decision": null,
    "expenseCategories": [],
    "modules": {
      "billing": true
    },
    "routes": [
      "/api/hr/documents"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "hr.payroll_file_route",
    "module.billing_on"
  ],
  "observation": "HR document action requires HR/admin/customer owner role"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [],
    "dataSignals": {
      "targetEmployeeId": "emp-002"
    },
    "decision": null,
    "expenseCategories": [],
    "modules": {},
    "routes": [
      "/api/hr/documents"
    ],
    "transportModes": []
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "hr.payroll_file_route"
  ],
  "observation": "HR document action requires HR/admin/customer owner role",
  "removedFragmentIds": [
    "module.billing_on"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `hr.payroll_file_route` (HR): HR document route is requested for another employee.
- `module.billing_on` (module entitlements): Billing module is enabled.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: round-up scenario violates hr.documents_customer_role_boundary

- Scenario: `roundup.support_hr_document_shortcut` (round-up)
- Fingerprint: `bayesilisk:5532829932331f02`
- Generated scenario: `false`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: HR document routes require customer HR/admin roles, not support/platform shortcuts.
- Observed result: `fail`
- Observation: HR document action requires HR/admin/customer owner role
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.774295`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `hr.payroll_file_route` [HR], complete alone: `false`
  - `module.billing_on` [module entitlements], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `roundup.support_hr_document_shortcut`: Support-flavored HR document shortcut composed from partial actor and HR route fragments.

Fingerprint: `bayesilisk:5532829932331f02`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: HR document routes require customer HR/admin roles, not support/platform shortcuts.

Observed: HR document action requires HR/admin/customer owner role

Risk score: 0.774295

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `hr.payroll_file_route` (HR): HR document route is requested for another employee.
- `module.billing_on` (module entitlements): Billing module is enabled.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: generated-round-up scenario violates travel.expense_items_match_itinerary

- Scenario: `generated.06.finance.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:b77585f0b1222977`
- Generated scenario: `true`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `fail`
- Observation: expense transport modes are not covered by itinerary legs
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.755519`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.06.finance.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:b77585f0b1222977`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: expense transport modes are not covered by itinerary legs

Risk score: 0.755519

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "finance",
    "businessFlow": [
      "travel funding request",
      "late travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": false,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "transportModesCoveredByItinerary": false
    },
    "decision": "approve",
    "expenseCategories": [
      "rental_car",
      "train"
    ],
    "modules": {
      "expenses": true,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "rental_car",
      "train"
    ]
  },
  "fragmentIds": [
    "role.finance",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.rental_car",
    "expense.train_ticket",
    "dms.foreign_tenant_document",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ],
  "observation": "expense transport modes are not covered by itinerary legs"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "transportModesCoveredByItinerary": false
    },
    "decision": null,
    "expenseCategories": [
      "train"
    ],
    "modules": {},
    "routes": [],
    "transportModes": [
      "train"
    ]
  },
  "fragmentIds": [
    "expense.train_ticket",
    "travel.legs_missing_airplane"
  ],
  "observation": "expense transport modes are not covered by itinerary legs",
  "removedFragmentIds": [
    "role.finance",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.rental_car",
    "dms.foreign_tenant_document",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: generated-round-up scenario violates travel.expense_items_match_itinerary

- Scenario: `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:f20a4ef0f2b751a6`
- Generated scenario: `true`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `fail`
- Observation: expense transport modes are not covered by itinerary legs
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.755519`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:f20a4ef0f2b751a6`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: expense transport modes are not covered by itinerary legs

Risk score: 0.755519

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Original generated scenario:
```json
{
  "accessPattern": {
    "actorRole": "support",
    "businessFlow": [
      "travel funding request",
      "late travel funding approval"
    ],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "documentTenantMatches": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "transportModesCoveredByItinerary": false
    },
    "decision": "approve",
    "expenseCategories": [
      "airplane",
      "train"
    ],
    "modules": {
      "expenses": true,
      "travel": true
    },
    "routes": [
      "/api/travel/funding-requests",
      "/api/expense-claims/{claimId}/review"
    ],
    "transportModes": [
      "airplane",
      "train"
    ]
  },
  "fragmentIds": [
    "role.support_takeover_expired",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.airfare",
    "expense.train_ticket",
    "dms.wrong_process_document",
    "travel.legs_missing_airplane",
    "creative.travel_expense_roundup"
  ],
  "observation": "expense transport modes are not covered by itinerary legs"
}
```

Minimized reproducer:
```json
{
  "accessPattern": {
    "actorRole": "unknown",
    "businessFlow": [],
    "dataSignals": {
      "allRequiredReceiptsUsable": true,
      "itineraryCoversExpenseDates": true,
      "segmentsChronological": true,
      "transportModesCoveredByItinerary": false
    },
    "decision": null,
    "expenseCategories": [
      "train"
    ],
    "modules": {},
    "routes": [],
    "transportModes": [
      "train"
    ]
  },
  "fragmentIds": [
    "expense.train_ticket",
    "travel.legs_missing_airplane"
  ],
  "observation": "expense transport modes are not covered by itinerary legs",
  "removedFragmentIds": [
    "role.support_takeover_expired",
    "module.travel_on",
    "module.expenses_on",
    "route.travel_funding_request",
    "travel.funding_approved_late",
    "route.expense_approve",
    "expense.airfare",
    "dms.wrong_process_document",
    "creative.travel_expense_roundup"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: intentionally-inconsistent scenario violates travel.expense_items_match_itinerary

- Scenario: `inconsistent.employee_self_review_bad_itinerary` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:aac4ace530f9b98b`
- Generated scenario: `false`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `fail`
- Observation: transport expense is attached to non-chronological itinerary legs
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.755519`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `travel.inconsistent_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.employee_self_review_bad_itinerary`: Employee self-approval is paired with an impossible itinerary.

Fingerprint: `bayesilisk:aac4ace530f9b98b`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: transport expense is attached to non-chronological itinerary legs

Risk score: 0.755519

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `travel.inconsistent_itinerary` (Travel): Travel itinerary ends before it starts and contains non-chronological legs.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: intentionally-inconsistent scenario violates travel.expense_items_match_itinerary

- Scenario: `inconsistent.travel_air_train_leg_mismatch` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:ee5270b63a75a152`
- Generated scenario: `false`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `fail`
- Observation: transport expense is attached to non-chronological itinerary legs
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.755519`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.inconsistent_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.travel_air_train_leg_mismatch`: Airplane and train expenses are attached to reversed travel dates and mismatched legs.

Fingerprint: `bayesilisk:ee5270b63a75a152`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: transport expense is attached to non-chronological itinerary legs

Risk score: 0.755519

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.inconsistent_itinerary` (Travel): Travel itinerary ends before it starts and contains non-chronological legs.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk breakage.hard-to-find: intentionally-inconsistent scenario violates travel.expense_items_match_itinerary

- Scenario: `inconsistent.travel_missing_airplane_leg` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:0ac9e9138945552a`
- Generated scenario: `false`
- Classification: `breakage.hard-to-find`
- Issue readiness: `ready-for-issue`
- Posterior mode: `harder-to-find-after-easy-breakages`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `fail`
- Observation: expense transport modes are not covered by itinerary legs
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.755519`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.travel_missing_airplane_leg`: Airfare is claimed against a chronological itinerary that lacks an airplane leg.

Fingerprint: `bayesilisk:0ac9e9138945552a`

Classification: `breakage.hard-to-find`

Issue readiness: `ready-for-issue`

Posterior mode: `harder-to-find-after-easy-breakages`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: expense transport modes are not covered by itinerary legs

Risk score: 0.755519

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk finding.candidate-breakage: intentionally-inconsistent scenario violates travel.itinerary_chronology

- Scenario: `inconsistent.employee_self_review_bad_itinerary` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:625e11b1979d5ec4`
- Generated scenario: `false`
- Classification: `finding.candidate-breakage`
- Issue readiness: `probe-only`
- Posterior mode: `fault-probability-elevated`
- Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.
- Observed result: `fail`
- Observation: itinerary is inconsistent or non-chronological
- Observation basis: `fresh-prior`
- Attention score: `0.337000`
- Attention reasons: `untested-plane`
- Risk score: `0.707987`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `travel.inconsistent_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.employee_self_review_bad_itinerary`: Employee self-approval is paired with an impossible itinerary.

Fingerprint: `bayesilisk:625e11b1979d5ec4`

Classification: `finding.candidate-breakage`

Issue readiness: `probe-only`

Posterior mode: `fault-probability-elevated`

Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.

Observed: itinerary is inconsistent or non-chronological

Risk score: 0.707987

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `travel.inconsistent_itinerary` (Travel): Travel itinerary ends before it starts and contains non-chronological legs.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk finding.candidate-breakage: intentionally-inconsistent scenario violates travel.itinerary_chronology

- Scenario: `inconsistent.travel_air_train_leg_mismatch` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:595dc90a1d468603`
- Generated scenario: `false`
- Classification: `finding.candidate-breakage`
- Issue readiness: `probe-only`
- Posterior mode: `fault-probability-elevated`
- Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.
- Observed result: `fail`
- Observation: itinerary is inconsistent or non-chronological
- Observation basis: `fresh-prior`
- Attention score: `0.337000`
- Attention reasons: `untested-plane`
- Risk score: `0.707987`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.inconsistent_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.travel_air_train_leg_mismatch`: Airplane and train expenses are attached to reversed travel dates and mismatched legs.

Fingerprint: `bayesilisk:595dc90a1d468603`

Classification: `finding.candidate-breakage`

Issue readiness: `probe-only`

Posterior mode: `fault-probability-elevated`

Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.

Observed: itinerary is inconsistent or non-chronological

Risk score: 0.707987

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.inconsistent_itinerary` (Travel): Travel itinerary ends before it starts and contains non-chronological legs.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-round-up scenario confirms roles.route_matrix_allowed

- Scenario: `generated.06.finance.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:09186ead644d0542`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.06.finance.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:09186ead644d0542`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-grassmann-attention scenario confirms roles.route_matrix_allowed

- Scenario: `generated.attention.02.dms_tenant_process_boundary` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:99c374fde29516d3`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.02.dms_tenant_process_boundary`: Grassmann-attention foreign DMS evidence probe

Fingerprint: `bayesilisk:99c374fde29516d3`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-grassmann-attention scenario confirms roles.route_matrix_allowed

- Scenario: `generated.attention.04.modules_expense_approval_requires_module_and_receipt` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:09b814abd14209c1`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.04.modules_expense_approval_requires_module_and_receipt`: Grassmann-attention disabled expense approval probe

Fingerprint: `bayesilisk:09b814abd14209c1`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: intentionally-inconsistent scenario confirms roles.route_matrix_allowed

- Scenario: `inconsistent.dms_wrong_process_receipt` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:4c26430a39bc244e`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.dms_wrong_process_receipt`: Tenant-scoped DMS evidence comes from the recruiting process during travel expense review.

Fingerprint: `bayesilisk:4c26430a39bc244e`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: intentionally-inconsistent scenario confirms roles.route_matrix_allowed

- Scenario: `inconsistent.travel_air_train_leg_mismatch` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:c8949550b02634ee`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.inconsistent_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.travel_air_train_leg_mismatch`: Airplane and train expenses are attached to reversed travel dates and mismatched legs.

Fingerprint: `bayesilisk:c8949550b02634ee`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.inconsistent_itinerary` (Travel): Travel itinerary ends before it starts and contains non-chronological legs.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: intentionally-inconsistent scenario confirms roles.route_matrix_allowed

- Scenario: `inconsistent.travel_missing_airplane_leg` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:be2e6ac7d943de74`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.travel_missing_airplane_leg`: Airfare is claimed against a chronological itinerary that lacks an airplane leg.

Fingerprint: `bayesilisk:be2e6ac7d943de74`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms roles.route_matrix_allowed

- Scenario: `mundane.billing_export_by_finance` (mundane)
- Fingerprint: `bayesilisk:cc773b5c04772ba3`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.billing_on` [module entitlements], complete alone: `false`
  - `billing.export_route` [Billing], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/billing/exports"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `mundane.billing_export_by_finance`: Finance exports billing data with the billing module enabled.

Fingerprint: `bayesilisk:cc773b5c04772ba3`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/billing/exports"
  ],
  "transportModes": []
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.billing_on` (module entitlements): Billing module is enabled.
- `billing.export_route` (Billing): Billing export route is requested.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms roles.route_matrix_allowed

- Scenario: `mundane.hr_document_by_hr_manager` (mundane)
- Fingerprint: `bayesilisk:4633ba556c769024`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.hr_manager` [HR], complete alone: `false`
  - `hr.payroll_file_route` [HR], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "hr_manager",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `mundane.hr_document_by_hr_manager`: Customer HR manager downloads an HR document through the customer HR route.

Fingerprint: `bayesilisk:4633ba556c769024`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "hr_manager",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Fragments:
- `role.hr_manager` (HR): Customer HR manager actor reviews personnel documents.
- `hr.payroll_file_route` (HR): HR document route is requested for another employee.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms roles.route_matrix_allowed

- Scenario: `mundane.manager_reviews_employee_expense` (mundane)
- Fingerprint: `bayesilisk:9573dbab2c7c903e`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.manager_reviewer` [Expenses], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "manager",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-002",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `mundane.manager_reviews_employee_expense`: Manager reviews a different employee's expense with usable evidence.

Fingerprint: `bayesilisk:9573dbab2c7c903e`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "manager",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-002",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.manager_reviewer` (Expenses): Manager actor reviews a different employee's expense claim.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms roles.route_matrix_allowed

- Scenario: `mundane.support_takeover_active_control` (mundane)
- Fingerprint: `bayesilisk:78fe9ff60640f16c`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: no actor/route access pattern to evaluate
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.support_takeover_active` [Support], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `mundane.support_takeover_active_control`: Support actor has an active non-expired takeover session with no customer data route.

Fingerprint: `bayesilisk:78fe9ff60640f16c`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: no actor/route access pattern to evaluate

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_active` (Support): Support actor has an active non-expired takeover session.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms roles.route_matrix_allowed

- Scenario: `mundane.travel_funding_to_multimodal_expense` (mundane)
- Fingerprint: `bayesilisk:455e81c9b9bc09b0`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `mundane.travel_funding_to_multimodal_expense`: Travel funding request is approved before rental car, train, and airplane expenses.

Fingerprint: `bayesilisk:455e81c9b9bc09b0`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved` (Travel): Travel funding is approved before expenses are submitted.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: round-up scenario confirms roles.route_matrix_allowed

- Scenario: `roundup.billing_export_disabled_module` (round-up)
- Fingerprint: `bayesilisk:f7c7e97496c474cf`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.billing_off` [module entitlements], complete alone: `false`
  - `billing.export_route` [Billing], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": false
  },
  "routes": [
    "/api/billing/exports"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `roundup.billing_export_disabled_module`: Finance actor reaches billing export while the billing module is disabled.

Fingerprint: `bayesilisk:f7c7e97496c474cf`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": false
  },
  "routes": [
    "/api/billing/exports"
  ],
  "transportModes": []
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.billing_off` (module entitlements): Billing module is disabled.
- `billing.export_route` (Billing): Billing export route is requested.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: round-up scenario confirms roles.route_matrix_allowed

- Scenario: `roundup.expense_missing_receipt_disabled_module` (round-up)
- Fingerprint: `bayesilisk:cda76488a39a8931`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `roundup.expense_missing_receipt_disabled_module`: Expense approval composed from disabled module, missing receipt, and travel context.

Fingerprint: `bayesilisk:cda76488a39a8931`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: round-up scenario confirms roles.route_matrix_allowed

- Scenario: `roundup.travel_expense_before_late_funding` (round-up)
- Fingerprint: `bayesilisk:7861f12725951c12`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `roundup.travel_expense_before_late_funding`: Travel expense is submitted before a late funding approval lands.

Fingerprint: `bayesilisk:7861f12725951c12`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: round-up scenario confirms roles.route_matrix_allowed

- Scenario: `roundup.travel_funding_unapproved_multimodal_expense` (round-up)
- Fingerprint: `bayesilisk:257bedbe3fa2d60f`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Every generated access pattern must use a role allowed by the route matrix.
- Observed result: `pass`
- Observation: actor role is allowed for all requested routes
- Observation basis: `invariant-adjustment:roles.route_matrix_allowed`
- Attention score: `0.435000`
- Attention reasons: `untested-plane, sensitive-invariant-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.460815`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_missing` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `roundup.travel_funding_unapproved_multimodal_expense`: Rental car, train, and airplane expenses are approved after a funding request with no approval.

Fingerprint: `bayesilisk:257bedbe3fa2d60f`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Every generated access pattern must use a role allowed by the route matrix.

Observed: actor role is allowed for all requested routes

Risk score: 0.460815

Observation basis:
```json
{
  "priorDelta": 0.18,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:roles.route_matrix_allowed"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_missing` (Travel): Travel funding request exists but has no approval.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-grassmann-attention scenario confirms dms.tenant_process_boundary

- Scenario: `generated.attention.04.modules_expense_approval_requires_module_and_receipt` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:0c6ecd506b9adf84`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `pass`
- Observation: DMS document is tenant-scoped and usable
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.318087`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.04.modules_expense_approval_requires_module_and_receipt`: Grassmann-attention disabled expense approval probe

Fingerprint: `bayesilisk:0c6ecd506b9adf84`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document is tenant-scoped and usable

Risk score: 0.318087

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "documentTenantMatches": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: intentionally-inconsistent scenario confirms dms.tenant_process_boundary

- Scenario: `inconsistent.employee_self_review_bad_itinerary` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:4ffb27a03c6756a5`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `pass`
- Observation: DMS document is tenant-scoped and usable
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.318087`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `travel.inconsistent_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.employee_self_review_bad_itinerary`: Employee self-approval is paired with an impossible itinerary.

Fingerprint: `bayesilisk:4ffb27a03c6756a5`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document is tenant-scoped and usable

Risk score: 0.318087

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {},
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `travel.inconsistent_itinerary` (Travel): Travel itinerary ends before it starts and contains non-chronological legs.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: intentionally-inconsistent scenario confirms dms.tenant_process_boundary

- Scenario: `inconsistent.travel_air_train_leg_mismatch` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:9fd1de837f0078b2`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `pass`
- Observation: DMS document is tenant-scoped and usable
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.318087`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.inconsistent_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.travel_air_train_leg_mismatch`: Airplane and train expenses are attached to reversed travel dates and mismatched legs.

Fingerprint: `bayesilisk:9fd1de837f0078b2`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document is tenant-scoped and usable

Risk score: 0.318087

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.inconsistent_itinerary` (Travel): Travel itinerary ends before it starts and contains non-chronological legs.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: intentionally-inconsistent scenario confirms dms.tenant_process_boundary

- Scenario: `inconsistent.travel_missing_airplane_leg` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:75624f4296e93667`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `pass`
- Observation: DMS document is tenant-scoped and usable
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.318087`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.travel_missing_airplane_leg`: Airfare is claimed against a chronological itinerary that lacks an airplane leg.

Fingerprint: `bayesilisk:75624f4296e93667`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document is tenant-scoped and usable

Risk score: 0.318087

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms dms.tenant_process_boundary

- Scenario: `mundane.manager_reviews_employee_expense` (mundane)
- Fingerprint: `bayesilisk:9a6354a39fae1901`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `pass`
- Observation: DMS document is tenant-scoped and usable
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.318087`
- Sub-scenarios:
  - `role.manager_reviewer` [Expenses], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "manager",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-002",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `mundane.manager_reviews_employee_expense`: Manager reviews a different employee's expense with usable evidence.

Fingerprint: `bayesilisk:9a6354a39fae1901`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document is tenant-scoped and usable

Risk score: 0.318087

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "manager",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-002",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.manager_reviewer` (Expenses): Manager actor reviews a different employee's expense claim.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms dms.tenant_process_boundary

- Scenario: `mundane.travel_funding_to_multimodal_expense` (mundane)
- Fingerprint: `bayesilisk:edff7859369bd2fc`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: DMS evidence must stay in tenant and approved process boundaries.
- Observed result: `pass`
- Observation: DMS document is tenant-scoped and usable
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.318087`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `mundane.travel_funding_to_multimodal_expense`: Travel funding request is approved before rental car, train, and airplane expenses.

Fingerprint: `bayesilisk:edff7859369bd2fc`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: DMS evidence must stay in tenant and approved process boundaries.

Observed: DMS document is tenant-scoped and usable

Risk score: 0.318087

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved` (Travel): Travel funding is approved before expenses are submitted.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-round-up scenario confirms modules.expense_approval_requires_module_and_receipt

- Scenario: `generated.06.finance.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:b41a45f3d63c4f6c`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `pass`
- Observation: expense approval has module entitlement and usable required receipts
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.259615`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.06.finance.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:b41a45f3d63c4f6c`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval has module entitlement and usable required receipts

Risk score: 0.259615

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-round-up scenario confirms modules.expense_approval_requires_module_and_receipt

- Scenario: `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:363bb0d5987c6e01`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `pass`
- Observation: expense approval has module entitlement and usable required receipts
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.259615`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:363bb0d5987c6e01`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval has module entitlement and usable required receipts

Risk score: 0.259615

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-grassmann-attention scenario confirms modules.expense_approval_requires_module_and_receipt

- Scenario: `generated.attention.02.dms_tenant_process_boundary` (generated-grassmann-attention)
- Fingerprint: `bayesilisk:af547e9e8dea8508`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `pass`
- Observation: expense approval has module entitlement and usable required receipts
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.259615`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.attention.02.dms_tenant_process_boundary`: Grassmann-attention foreign DMS evidence probe

Fingerprint: `bayesilisk:af547e9e8dea8508`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval has module entitlement and usable required receipts

Risk score: 0.259615

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: intentionally-inconsistent scenario confirms modules.expense_approval_requires_module_and_receipt

- Scenario: `inconsistent.dms_wrong_process_receipt` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:1706a5d37fff2e00`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `pass`
- Observation: expense approval has module entitlement and usable required receipts
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.259615`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.dms_wrong_process_receipt`: Tenant-scoped DMS evidence comes from the recruiting process during travel expense review.

Fingerprint: `bayesilisk:1706a5d37fff2e00`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval has module entitlement and usable required receipts

Risk score: 0.259615

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: intentionally-inconsistent scenario confirms modules.expense_approval_requires_module_and_receipt

- Scenario: `inconsistent.travel_air_train_leg_mismatch` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:4a4184a04249a67f`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `pass`
- Observation: expense approval has module entitlement and usable required receipts
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.259615`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.inconsistent_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.travel_air_train_leg_mismatch`: Airplane and train expenses are attached to reversed travel dates and mismatched legs.

Fingerprint: `bayesilisk:4a4184a04249a67f`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval has module entitlement and usable required receipts

Risk score: 0.259615

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": false,
    "segmentsChronological": false,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.inconsistent_itinerary` (Travel): Travel itinerary ends before it starts and contains non-chronological legs.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: intentionally-inconsistent scenario confirms modules.expense_approval_requires_module_and_receipt

- Scenario: `inconsistent.travel_missing_airplane_leg` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:144e40938b277344`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `pass`
- Observation: expense approval has module entitlement and usable required receipts
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.259615`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.travel_missing_airplane_leg`: Airfare is claimed against a chronological itinerary that lacks an airplane leg.

Fingerprint: `bayesilisk:144e40938b277344`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval has module entitlement and usable required receipts

Risk score: 0.259615

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms modules.expense_approval_requires_module_and_receipt

- Scenario: `mundane.manager_reviews_employee_expense` (mundane)
- Fingerprint: `bayesilisk:fa888535553cf31f`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `pass`
- Observation: expense approval has module entitlement and usable required receipts
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.259615`
- Sub-scenarios:
  - `role.manager_reviewer` [Expenses], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "manager",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-002",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `mundane.manager_reviews_employee_expense`: Manager reviews a different employee's expense with usable evidence.

Fingerprint: `bayesilisk:fa888535553cf31f`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval has module entitlement and usable required receipts

Risk score: 0.259615

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "manager",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-002",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.manager_reviewer` (Expenses): Manager actor reviews a different employee's expense claim.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms modules.expense_approval_requires_module_and_receipt

- Scenario: `mundane.travel_funding_to_multimodal_expense` (mundane)
- Fingerprint: `bayesilisk:5012613256468dc3`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `pass`
- Observation: expense approval has module entitlement and usable required receipts
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.259615`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `mundane.travel_funding_to_multimodal_expense`: Travel funding request is approved before rental car, train, and airplane expenses.

Fingerprint: `bayesilisk:5012613256468dc3`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval has module entitlement and usable required receipts

Risk score: 0.259615

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved` (Travel): Travel funding is approved before expenses are submitted.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: round-up scenario confirms modules.expense_approval_requires_module_and_receipt

- Scenario: `roundup.travel_expense_before_late_funding` (round-up)
- Fingerprint: `bayesilisk:ac09b779336e2653`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `pass`
- Observation: expense approval has module entitlement and usable required receipts
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.259615`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `roundup.travel_expense_before_late_funding`: Travel expense is submitted before a late funding approval lands.

Fingerprint: `bayesilisk:ac09b779336e2653`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval has module entitlement and usable required receipts

Risk score: 0.259615

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: round-up scenario confirms modules.expense_approval_requires_module_and_receipt

- Scenario: `roundup.travel_funding_unapproved_multimodal_expense` (round-up)
- Fingerprint: `bayesilisk:c9a659e80e72a9e2`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.
- Observed result: `pass`
- Observation: expense approval has module entitlement and usable required receipts
- Observation basis: `fresh-prior`
- Attention score: `0.379000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.259615`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_missing` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `roundup.travel_funding_unapproved_multimodal_expense`: Rental car, train, and airplane expenses are approved after a funding request with no approval.

Fingerprint: `bayesilisk:c9a659e80e72a9e2`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Expense approvals require expenses entitlement and usable required receipt evidence.

Observed: expense approval has module entitlement and usable required receipts

Risk score: 0.259615

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_missing` (Travel): Travel funding request exists but has no approval.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: creative scenario confirms support.takeover_session_required

- Scenario: `creative.support_active_hr_document_shortcut` (creative)
- Fingerprint: `bayesilisk:782f914278e4c320`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Support access requires active non-expired takeover scope.
- Observed result: `pass`
- Observation: support takeover session is active
- Observation basis: `fresh-prior`
- Attention score: `0.376000`
- Attention reasons: `untested-plane`
- Risk score: `0.256637`
- Sub-scenarios:
  - `role.support_takeover_active` [Support], complete alone: `false`
  - `hr.payroll_file_route` [HR], complete alone: `false`
  - `module.billing_on` [module entitlements], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `creative.support_active_hr_document_shortcut`: Active support takeover is still not a customer HR role for HR document download.

Fingerprint: `bayesilisk:782f914278e4c320`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Support access requires active non-expired takeover scope.

Observed: support takeover session is active

Risk score: 0.256637

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_active` (Support): Support actor has an active non-expired takeover session.
- `hr.payroll_file_route` (HR): HR document route is requested for another employee.
- `module.billing_on` (module entitlements): Billing module is enabled.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms support.takeover_session_required

- Scenario: `mundane.support_takeover_active_control` (mundane)
- Fingerprint: `bayesilisk:168aaa56a8772263`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Support access requires active non-expired takeover scope.
- Observed result: `pass`
- Observation: support takeover session is active
- Observation basis: `fresh-prior`
- Attention score: `0.376000`
- Attention reasons: `untested-plane`
- Risk score: `0.256637`
- Sub-scenarios:
  - `role.support_takeover_active` [Support], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `mundane.support_takeover_active_control`: Support actor has an active non-expired takeover session with no customer data route.

Fingerprint: `bayesilisk:168aaa56a8772263`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Support access requires active non-expired takeover scope.

Observed: support takeover session is active

Risk score: 0.256637

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [],
  "transportModes": []
}
```

Fragments:
- `role.support_takeover_active` (Support): Support actor has an active non-expired takeover session.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms billing.export_requires_role_and_module

- Scenario: `mundane.billing_export_by_finance` (mundane)
- Fingerprint: `bayesilisk:5f21038fc640b4c7`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Billing exports require billing entitlement and finance/admin role.
- Observed result: `pass`
- Observation: billing export has module and role entitlement
- Observation basis: `fresh-prior`
- Attention score: `0.361000`
- Attention reasons: `untested-plane`
- Risk score: `0.256356`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.billing_on` [module entitlements], complete alone: `false`
  - `billing.export_route` [Billing], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/billing/exports"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `mundane.billing_export_by_finance`: Finance exports billing data with the billing module enabled.

Fingerprint: `bayesilisk:5f21038fc640b4c7`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Billing exports require billing entitlement and finance/admin role.

Observed: billing export has module and role entitlement

Risk score: 0.256356

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {},
  "decision": null,
  "expenseCategories": [],
  "modules": {
    "billing": true
  },
  "routes": [
    "/api/billing/exports"
  ],
  "transportModes": []
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.billing_on` (module entitlements): Billing module is enabled.
- `billing.export_route` (Billing): Billing export route is requested.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms hr.documents_customer_role_boundary

- Scenario: `mundane.hr_document_by_hr_manager` (mundane)
- Fingerprint: `bayesilisk:d59128fa16a01591`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: HR document routes require customer HR/admin roles, not support/platform shortcuts.
- Observed result: `pass`
- Observation: HR document route has a customer HR/admin role
- Observation basis: `fresh-prior`
- Attention score: `0.388000`
- Attention reasons: `untested-plane, sensitive-invariant-plane`
- Risk score: `0.254902`
- Sub-scenarios:
  - `role.hr_manager` [HR], complete alone: `false`
  - `hr.payroll_file_route` [HR], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "hr_manager",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `mundane.hr_document_by_hr_manager`: Customer HR manager downloads an HR document through the customer HR route.

Fingerprint: `bayesilisk:d59128fa16a01591`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: HR document routes require customer HR/admin roles, not support/platform shortcuts.

Observed: HR document route has a customer HR/admin role

Risk score: 0.254902

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "hr_manager",
  "businessFlow": [],
  "dataSignals": {
    "targetEmployeeId": "emp-002"
  },
  "decision": null,
  "expenseCategories": [],
  "modules": {},
  "routes": [
    "/api/hr/documents"
  ],
  "transportModes": []
}
```

Fragments:
- `role.hr_manager` (HR): Customer HR manager actor reviews personnel documents.
- `hr.payroll_file_route` (HR): HR document route is requested for another employee.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms roles.employee_self_review_forbidden

- Scenario: `mundane.manager_reviews_employee_expense` (mundane)
- Fingerprint: `bayesilisk:f366b0ed1dc75f2c`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Employee self-review remains forbidden for approvals.
- Observed result: `pass`
- Observation: actor and target employee are separated
- Observation basis: `fresh-prior`
- Attention score: `0.373000`
- Attention reasons: `untested-plane`
- Risk score: `0.237094`
- Sub-scenarios:
  - `role.manager_reviewer` [Expenses], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "manager",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-002",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `mundane.manager_reviews_employee_expense`: Manager reviews a different employee's expense with usable evidence.

Fingerprint: `bayesilisk:f366b0ed1dc75f2c`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Employee self-review remains forbidden for approvals.

Observed: actor and target employee are separated

Risk score: 0.237094

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "manager",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-002",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.manager_reviewer` (Expenses): Manager actor reviews a different employee's expense claim.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-round-up scenario confirms travel.itinerary_chronology

- Scenario: `generated.05.employee_self.funding_approved.legs_consistent_multimodal` (generated-round-up)
- Fingerprint: `bayesilisk:77044f4b2095a7cc`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.
- Observed result: `pass`
- Observation: itinerary dates and segments are chronological
- Observation basis: `fresh-prior`
- Attention score: `0.337000`
- Attention reasons: `untested-plane`
- Risk score: `0.230354`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.05.employee_self.funding_approved.legs_consistent_multimodal`: Generated composite travel expense probe

Fingerprint: `bayesilisk:77044f4b2095a7cc`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.

Observed: itinerary dates and segments are chronological

Risk score: 0.230354

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved` (Travel): Travel funding is approved before expenses are submitted.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-round-up scenario confirms travel.itinerary_chronology

- Scenario: `generated.06.finance.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:fa9fee08a4ed71bd`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.
- Observed result: `pass`
- Observation: itinerary dates and segments are chronological
- Observation basis: `fresh-prior`
- Attention score: `0.337000`
- Attention reasons: `untested-plane`
- Risk score: `0.230354`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.foreign_tenant_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.06.finance.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:fa9fee08a4ed71bd`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.

Observed: itinerary dates and segments are chronological

Risk score: 0.230354

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.foreign_tenant_document` (DMS): DMS document belongs to another tenant.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-round-up scenario confirms travel.itinerary_chronology

- Scenario: `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane` (generated-round-up)
- Fingerprint: `bayesilisk:be66c10125a65d5f`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.
- Observed result: `pass`
- Observation: itinerary dates and segments are chronological
- Observation basis: `fresh-prior`
- Attention score: `0.337000`
- Attention reasons: `untested-plane`
- Risk score: `0.230354`
- Sub-scenarios:
  - `role.support_takeover_expired` [Support], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.07.support_takeover_expired.funding_approved_late.legs_missing_airplane`: Generated composite travel expense probe

Fingerprint: `bayesilisk:be66c10125a65d5f`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.

Observed: itinerary dates and segments are chronological

Risk score: 0.230354

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "support",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Fragments:
- `role.support_takeover_expired` (Support): Support actor has an expired takeover session.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-round-up scenario confirms travel.itinerary_chronology

- Scenario: `generated.08.employee_self.funding_missing.mundane_itinerary` (generated-round-up)
- Fingerprint: `bayesilisk:fb79ca447a0194a7`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.
- Observed result: `pass`
- Observation: itinerary dates and segments are chronological
- Observation basis: `fresh-prior`
- Attention score: `0.337000`
- Attention reasons: `untested-plane`
- Risk score: `0.230354`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_missing` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.08.employee_self.funding_missing.mundane_itinerary`: Generated composite travel expense probe

Fingerprint: `bayesilisk:fb79ca447a0194a7`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.

Observed: itinerary dates and segments are chronological

Risk score: 0.230354

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_missing` (Travel): Travel funding request exists but has no approval.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: intentionally-inconsistent scenario confirms travel.itinerary_chronology

- Scenario: `inconsistent.travel_missing_airplane_leg` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:e1b7bd40a2fc2c37`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.
- Observed result: `pass`
- Observation: itinerary dates and segments are chronological
- Observation basis: `fresh-prior`
- Attention score: `0.337000`
- Attention reasons: `untested-plane`
- Risk score: `0.230354`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_missing_airplane` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.travel_missing_airplane_leg`: Airfare is claimed against a chronological itinerary that lacks an airplane leg.

Fingerprint: `bayesilisk:e1b7bd40a2fc2c37`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.

Observed: itinerary dates and segments are chronological

Risk score: 0.230354

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": false
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_missing_airplane` (Travel): Travel itinerary is chronological but lacks an airplane leg for airfare.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: round-up scenario confirms travel.itinerary_chronology

- Scenario: `roundup.expense_missing_receipt_disabled_module` (round-up)
- Fingerprint: `bayesilisk:1cbe6bf36a1fef6e`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.
- Observed result: `pass`
- Observation: itinerary dates and segments are chronological
- Observation basis: `fresh-prior`
- Attention score: `0.337000`
- Attention reasons: `untested-plane`
- Risk score: `0.230354`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.receipt_missing` [Expenses], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Suggested issue body:

````markdown
Scenario `roundup.expense_missing_receipt_disabled_module`: Expense approval composed from disabled module, missing receipt, and travel context.

Fingerprint: `bayesilisk:1cbe6bf36a1fef6e`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Travel scenarios must not silently accept inconsistent itineraries.

Observed: itinerary dates and segments are chronological

Risk score: 0.230354

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": false,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [],
  "modules": {
    "expenses": false
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": []
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.receipt_missing` (Expenses): Hotel claim item has no usable linked DMS receipt.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-round-up scenario confirms travel.funding_before_expense

- Scenario: `generated.05.employee_self.funding_approved.legs_consistent_multimodal` (generated-round-up)
- Fingerprint: `bayesilisk:5bb0ab94812c039d`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Travel expenses require approved funding before expense submission or approval.
- Observed result: `pass`
- Observation: travel funding is approved before expense review
- Observation basis: `invariant-adjustment:travel.funding_before_expense`
- Attention score: `0.354333`
- Attention reasons: `untested-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.222200`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.05.employee_self.funding_approved.legs_consistent_multimodal`: Generated composite travel expense probe

Fingerprint: `bayesilisk:5bb0ab94812c039d`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Travel expenses require approved funding before expense submission or approval.

Observed: travel funding is approved before expense review

Risk score: 0.222200

Observation basis:
```json
{
  "priorDelta": 0.018,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:travel.funding_before_expense"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved` (Travel): Travel funding is approved before expenses are submitted.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms travel.funding_before_expense

- Scenario: `mundane.travel_funding_to_multimodal_expense` (mundane)
- Fingerprint: `bayesilisk:6820d7398a1ef242`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Travel expenses require approved funding before expense submission or approval.
- Observed result: `pass`
- Observation: travel funding is approved before expense review
- Observation basis: `invariant-adjustment:travel.funding_before_expense`
- Attention score: `0.354333`
- Attention reasons: `untested-plane, context-keyword-near-plane, context-prior-adjustment`
- Risk score: `0.222200`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `mundane.travel_funding_to_multimodal_expense`: Travel funding request is approved before rental car, train, and airplane expenses.

Fingerprint: `bayesilisk:6820d7398a1ef242`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Travel expenses require approved funding before expense submission or approval.

Observed: travel funding is approved before expense review

Risk score: 0.222200

Observation basis:
```json
{
  "priorDelta": 0.018,
  "source": "calcom-playwright-probe",
  "tags": [
    "invariant-adjustment:travel.funding_before_expense"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved` (Travel): Travel funding is approved before expenses are submitted.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-round-up scenario confirms travel.expense_items_match_itinerary

- Scenario: `generated.05.employee_self.funding_approved.legs_consistent_multimodal` (generated-round-up)
- Fingerprint: `bayesilisk:b89d8428af20ca34`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `pass`
- Observation: transport expense dates and modes match the itinerary
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.216132`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.05.employee_self.funding_approved.legs_consistent_multimodal`: Generated composite travel expense probe

Fingerprint: `bayesilisk:b89d8428af20ca34`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: transport expense dates and modes match the itinerary

Risk score: 0.216132

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved` (Travel): Travel funding is approved before expenses are submitted.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: generated-round-up scenario confirms travel.expense_items_match_itinerary

- Scenario: `generated.08.employee_self.funding_missing.mundane_itinerary` (generated-round-up)
- Fingerprint: `bayesilisk:1a180865e864e2b4`
- Generated scenario: `true`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `pass`
- Observation: transport expense dates and modes match the itinerary
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.216132`
- Sub-scenarios:
  - `role.employee_self` [HR], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_off` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_missing` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
  - `creative.travel_expense_roundup` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `generated.08.employee_self.funding_missing.mundane_itinerary`: Generated composite travel expense probe

Fingerprint: `bayesilisk:1a180865e864e2b4`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: transport expense dates and modes match the itinerary

Risk score: 0.216132

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "employee",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-001",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "airplane",
    "train"
  ],
  "modules": {
    "expenses": false,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "airplane",
    "train"
  ]
}
```

Fragments:
- `role.employee_self` (HR): Employee actor targets their own record.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_off` (module entitlements): Expenses module is disabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_missing` (Travel): Travel funding request exists but has no approval.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.
- `creative.travel_expense_roundup` (Travel): Creative round-up composes travel, expense, support, and DMS fragments.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: intentionally-inconsistent scenario confirms travel.expense_items_match_itinerary

- Scenario: `inconsistent.dms_wrong_process_receipt` (intentionally-inconsistent)
- Fingerprint: `bayesilisk:35eec7bc1ab41458`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `pass`
- Observation: transport expense dates and modes match the itinerary
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.216132`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `dms.wrong_process_document` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Suggested issue body:

````markdown
Scenario `inconsistent.dms_wrong_process_receipt`: Tenant-scoped DMS evidence comes from the recruiting process during travel expense review.

Fingerprint: `bayesilisk:35eec7bc1ab41458`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: transport expense dates and modes match the itinerary

Risk score: 0.216132

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `dms.wrong_process_document` (DMS): DMS document is tenant-scoped but belongs to the wrong process.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms travel.expense_items_match_itinerary

- Scenario: `mundane.manager_reviews_employee_expense` (mundane)
- Fingerprint: `bayesilisk:c90a0c013cbff81b`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `pass`
- Observation: transport expense dates and modes match the itinerary
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.216132`
- Sub-scenarios:
  - `role.manager_reviewer` [Expenses], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "manager",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-002",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `mundane.manager_reviews_employee_expense`: Manager reviews a different employee's expense with usable evidence.

Fingerprint: `bayesilisk:c90a0c013cbff81b`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: transport expense dates and modes match the itinerary

Risk score: 0.216132

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "manager",
  "businessFlow": [],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "targetEmployeeId": "emp-002",
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true
  },
  "routes": [
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.manager_reviewer` (Expenses): Manager actor reviews a different employee's expense claim.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: mundane scenario confirms travel.expense_items_match_itinerary

- Scenario: `mundane.travel_funding_to_multimodal_expense` (mundane)
- Fingerprint: `bayesilisk:9e122ffbcbcfe525`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `pass`
- Observation: transport expense dates and modes match the itinerary
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.216132`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `mundane.travel_funding_to_multimodal_expense`: Travel funding request is approved before rental car, train, and airplane expenses.

Fingerprint: `bayesilisk:9e122ffbcbcfe525`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: transport expense dates and modes match the itinerary

Risk score: 0.216132

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved` (Travel): Travel funding is approved before expenses are submitted.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: round-up scenario confirms travel.expense_items_match_itinerary

- Scenario: `roundup.travel_expense_before_late_funding` (round-up)
- Fingerprint: `bayesilisk:e73bb4f4511f5897`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `pass`
- Observation: transport expense dates and modes match the itinerary
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.216132`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `route.travel_funding_approve` [Travel], complete alone: `false`
  - `travel.funding_approved_late` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.mundane_itinerary` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Suggested issue body:

````markdown
Scenario `roundup.travel_expense_before_late_funding`: Travel expense is submitted before a late funding approval lands.

Fingerprint: `bayesilisk:e73bb4f4511f5897`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: transport expense dates and modes match the itinerary

Risk score: 0.216132

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request",
    "late travel funding approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "train"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/travel/funding-requests/{requestId}/approve",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "train"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `route.travel_funding_approve` (Travel): Travel funding approval route receives an approve decision.
- `travel.funding_approved_late` (Travel): Travel funding is approved after the expense submission date.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.mundane_itinerary` (Travel): Travel itinerary is chronological.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````

### Bayesilisk control-confirmed: round-up scenario confirms travel.expense_items_match_itinerary

- Scenario: `roundup.travel_funding_unapproved_multimodal_expense` (round-up)
- Fingerprint: `bayesilisk:0eb43c130732740f`
- Generated scenario: `false`
- Classification: `control-confirmed`
- Issue readiness: `no-issue-control`
- Posterior mode: `posterior-control-confidence`
- Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.
- Observed result: `pass`
- Observation: transport expense dates and modes match the itinerary
- Observation basis: `fresh-prior`
- Attention score: `0.343000`
- Attention reasons: `untested-plane`
- Risk score: `0.216132`
- Sub-scenarios:
  - `role.finance` [Billing], complete alone: `false`
  - `module.travel_on` [module entitlements], complete alone: `false`
  - `module.expenses_on` [module entitlements], complete alone: `false`
  - `route.travel_funding_request` [Travel], complete alone: `false`
  - `travel.funding_missing` [Travel], complete alone: `false`
  - `route.expense_approve` [Expenses], complete alone: `false`
  - `expense.rental_car` [Expenses], complete alone: `false`
  - `expense.train_ticket` [Expenses], complete alone: `false`
  - `expense.airfare` [Expenses], complete alone: `false`
  - `dms.correct_receipt` [DMS], complete alone: `false`
  - `travel.legs_consistent_multimodal` [Travel], complete alone: `false`
- Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Suggested issue body:

````markdown
Scenario `roundup.travel_funding_unapproved_multimodal_expense`: Rental car, train, and airplane expenses are approved after a funding request with no approval.

Fingerprint: `bayesilisk:0eb43c130732740f`

Classification: `control-confirmed`

Issue readiness: `no-issue-control`

Posterior mode: `posterior-control-confidence`

Expected invariant: Rental car, train, and airplane expenses must match chronological itinerary legs.

Observed: transport expense dates and modes match the itinerary

Risk score: 0.216132

Observation basis:
```json
{
  "priorDelta": 0.0,
  "source": "calcom-playwright-probe",
  "tags": [
    "fresh-prior"
  ]
}
```

Access pattern:
```json
{
  "actorRole": "finance",
  "businessFlow": [
    "travel funding request without approval"
  ],
  "dataSignals": {
    "allRequiredReceiptsUsable": true,
    "documentTenantMatches": true,
    "itineraryCoversExpenseDates": true,
    "segmentsChronological": true,
    "transportModesCoveredByItinerary": true
  },
  "decision": "approve",
  "expenseCategories": [
    "rental_car",
    "train",
    "airplane"
  ],
  "modules": {
    "expenses": true,
    "travel": true
  },
  "routes": [
    "/api/travel/funding-requests",
    "/api/expense-claims/{claimId}/review"
  ],
  "transportModes": [
    "rental_car",
    "train",
    "airplane"
  ]
}
```

Fragments:
- `role.finance` (Billing): Finance actor with review and export intent.
- `module.travel_on` (module entitlements): Travel module is enabled.
- `module.expenses_on` (module entitlements): Expenses module is enabled for the organization.
- `route.travel_funding_request` (Travel): Travel funding request route receives a request.
- `travel.funding_missing` (Travel): Travel funding request exists but has no approval.
- `route.expense_approve` (Expenses): Expense review endpoint receives an approve decision.
- `expense.rental_car` (Expenses): Rental car expense has a usable receipt and a trip-date service date.
- `expense.train_ticket` (Expenses): Train ticket expense has a usable receipt.
- `expense.airfare` (Expenses): Airplane ticket expense has a usable receipt.
- `dms.correct_receipt` (DMS): DMS receipt is tenant-scoped and approved for travel expense.
- `travel.legs_consistent_multimodal` (Travel): Train, rental car, and airplane legs are chronological and cover expense dates.

Reproduce with `python3 -m bayesilisk --seed <seed> --format json`.
````
