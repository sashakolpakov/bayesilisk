# Examples

Worked examples live in the repository-level
[examples](https://github.com/sashakolpakov/bayesilisk/tree/main/examples)
folder.

Coding agents should ingest
[examples/connector-agent-contract.json](https://github.com/sashakolpakov/bayesilisk/blob/main/examples/connector-agent-contract.json)
before writing a connector. It lists the required source-context fields,
observed-evidence fields, allowed agent steps, and non-negotiable boundaries.

## Cal.com Connector Evidence

The [Cal.com example](https://github.com/sashakolpakov/bayesilisk/tree/main/examples/calcom)
shows Bayesilisk used with its general core and an app-specific connector. The
connector follows the documented contract: it supplies source facts, explicit
proposal rules, connector actions, expected statuses, and observed local
evidence. Bayesilisk expands only those supplied rules, then verifies
expected-versus-observed facts.

Captured evidence is included for Cal.com commit
`180ede28f0bddf2738933a6e60a8e80f6116d7da` from
`https://github.com/calcom/cal.com`.

The checked-in artifacts show:

- route source facts with explicit proposal rules;
- sequence source context with a connector-declared action graph;
- 7 Bayesilisk-generated proposals;
- 7 local connector observations;
- 7 connector-observed findings: 6 unknown/stale `rescheduleUid` route
  mutations where expected `404` was observed as `200`, plus 1 cancelled
  booking replay workflow where expected `409` was observed as `200`;
- app-only JSON, Markdown, and issue-payload reports;
- upstream issue and fix-PR references in `examples/calcom/upstream-outcomes.md`.

The upstream outcome references matter: an open fix PR linked to a Bayesilisk
finding is stronger validation than a closed issue by itself, because it shows
a human contributor found the report concrete enough to implement a targeted
change.

Explanatory prose in connector context may help Grassmann attention route and
rank the investigation, but proposal expansion comes from explicit rules and
verdicts come from observed evidence.
