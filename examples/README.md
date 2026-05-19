# Bayesilisk Examples

This directory contains worked connector examples and captured evidence.

Examples are not Bayesilisk core. They show how a test team can keep
application-specific fixture setup and action mapping outside the verifier while
feeding Bayesilisk source context, proposal rules, observed evidence, and
reports.

## Cal.com Connector Evidence

See [calcom/](calcom/) for a real-app connector example against a local Cal.com
checkout. The example includes:

- the Playwright connector used in the Cal.com test repo;
- source context with explicit proposal rules;
- sequence context with a connector-declared action graph;
- Bayesilisk-generated probe proposals;
- consolidated observed execution context;
- JSON, Markdown, and issue-payload reports.
- upstream issue and fix-PR references.

The Cal.com example records the exact upstream commit that was tested and the
expected-versus-observed failures found locally. The current clean run contains
7 app findings: 6 unknown/stale `rescheduleUid` route mutations and 1 generated
cancelled-booking replay workflow sequence. Upstream issue and PR references
are tracked as validation signals without keeping historical run logs.
