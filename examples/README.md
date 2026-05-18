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
- Bayesilisk-generated probe proposals;
- observed execution context;
- JSON, Markdown, and issue-payload reports.

The Cal.com example records the exact upstream commit that was tested and the
expected-versus-observed failures found locally.
