# Examples

Worked examples live in the repository-level
[examples](https://github.com/sashakolpakov/bayesilisk/tree/main/examples)
folder.

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

- 3 source facts that pass the connector contract;
- 6 Bayesilisk-generated proposals;
- 6 local connector observations;
- 6 connector-observed findings where expected `404` was observed as `200`;
- full JSON, Markdown, and issue-payload reports.

Explanatory prose in connector context may help Grassmann attention route and
rank the investigation, but proposal expansion comes from explicit rules and
verdicts come from observed evidence.
