# Connector Authoring

New to connectors? Start with the guided {doc}`connector-quickstart`, which walks
the `bayesilisk connector init -> validate -> propose -> verify` loop. This page
is the full reference for the underlying contract.

This page is for test teams writing connectors only. Do not modify Bayesilisk
core for an app integration. Keep all app knowledge in the target app, a test
repo, or a small connector package owned by the test team.

For coding agents and LLM teams, the machine-readable summary is
[examples/connector-agent-contract.json](https://github.com/sashakolpakov/bayesilisk/blob/main/examples/connector-agent-contract.json).
Use it as the ingestion contract before writing connector code.

The connector contract is now two-stage:

```text
app fixtures + app source context -> source context JSON
source context JSON -> bayesilisk context-derived probe proposals
probe proposals -> connector executes real app actions -> observed context JSON
observed context JSON -> bayesilisk report / issue payloads
```

Bayesilisk remains app-agnostic: it expands context-supplied proposal rules over
connector-declared routes, parameters, actors, and actions. The connector
remains app-specific: it maps `connectorAction` names to real fixture setup,
browser/API actions, and observed statuses.

## What Goes In A Connector

A connector may contain:

- app-specific fixture setup;
- app-specific login/session helpers;
- route rendering helpers;
- Playwright/Cypress actions;
- source-context extraction scripts;
- mappings from connector action names to real app actions;
- code that writes Bayesilisk context JSON.

A connector must not contain:

- Bayesilisk core patches;
- new Bayesilisk invariant engine code;
- code that marks a bug as verified without observed evidence;
- LLM-written `observedStatus`;
- LLM-written `passed`;
- production credentials or production data access.

## Minimal Output Contract

The connector writes a normal Bayesilisk context JSON file. The important part is
`repositoryFacts`.

```json
{
  "source": "my-app-playwright-connector",
  "agentNotes": [
    "Connector observed route behavior for a source-backed probe."
  ],
  "priorAdjustments": {},
  "repositoryFacts": [
    {
      "source": "repository-scan",
      "path": "app/routes/resource_action.ts",
      "title": "Resource action validates target identifier",
      "invariantId": "myapp.unknown_target_id_rejected",
      "routePattern": "/resource/{resourceId}/action?targetId={targetId}",
      "params": [
        {"name": "resourceId", "kind": "id", "location": "path", "required": true},
        {"name": "targetId", "kind": "id", "location": "query", "required": true}
      ],
      "expectedBehavior": {
        "description": "Unknown target IDs should return not found.",
        "status": 404
      },
      "proposalRules": {
        "targetId": [
          {"id": "unknown-id", "value": "missing-targetId"},
          {"id": "stale-id", "value": "stale-targetId"}
        ]
      },
      "availableActions": [
        "open-resource-action"
      ],
      "nearbyTests": [
        "direct route returns 404 when the target ID is missing"
      ],
      "sourceText": "TODO: force 404 when targetId is not found."
    },
    {
      "source": "microsoft-playwright",
      "title": "Unknown target identifier must not open protected action",
      "actorRole": "operator",
      "invariantId": "myapp.unknown_target_id_rejected",
      "route": "/resource/{resourceId}/action?targetId={targetId}",
      "expectedStatus": 404,
      "observedStatus": 200,
      "passed": false,
      "targetUrl": "http://localhost:3000/resource/123/action?targetId=missing",
      "failureDetail": "Unknown target ID was ignored and the protected action was visible.",
      "artifactPaths": [
        "/tmp/myapp-bayesilisk/proof.png"
      ],
      "networkResponses": [
        {
          "status": 200,
          "url": "http://localhost:3000/resource/123/action?targetId=missing"
        }
      ],
      "selector": "connector:open-resource-action",
      "timestamp": "2026-05-18T00:00:00Z"
    }
  ],
  "playwrightProbe": {
    "artifactCount": 1,
    "failedCount": 1,
    "passedCount": 0,
    "resultCount": 1,
    "target": "local my-app fixtures"
  }
}
```

The first fact is source context. The second fact is observed evidence. Bayesilisk
uses the source context for explanation and the observed fact for verification.

## Connector Workflow

1. Gather source-backed expectations.

Use existing tests, TODOs, route handlers, permission matrices, schemas, and
product rules. The expectation must be concrete enough to write an
`expectedStatus`.

Explanatory prose in fields such as `text`, `sourceText`, and `nearbyTests` can
help Grassmann attention route and rank the investigation. It is not a rule by
itself: Bayesilisk proposal expansion still requires `proposalRules` or
`proposalGates`, and Bayesilisk verdicts still require observed evidence.

2. Ask Bayesilisk for context-derived probe proposals.

```sh
python3 -m bayesilisk \
  --context /tmp/my-app-source-context.json \
  --probe-proposals-output /tmp/my-app-proposals.json
```

Bayesilisk applies finite-state proposal rules supplied by the context. A small
connector can put rules beside each fact in `proposalRules`; a larger connector
can put shared rules at top level in `proposalGates`. Rules are keyed by
parameter name, and values are deterministic mutation descriptors supplied by
the context.

Bayesilisk does not infer expected statuses, decide which parameters are
semantically valid to mutate, or invent app-specific mutated values. If no
`proposalRules` or matching `proposalGates` are supplied, it emits no proposals.

Do not add app-specific logic to Bayesilisk for a connector. Add app-specific
execution support in the connector by mapping proposal `connectorAction` values
to real app actions.

For longer deterministic workflows, a connector can also declare an action
graph. The connector still owns execution, but Bayesilisk can compose bounded
sequences from declared action inputs and outputs. Action-graph dependencies
must be ABAG typed tokens. Typed tokens separate the universal meaning from the
app-specific handle:

```json
{
  "token": "resource.public_id",
  "resourceType": "booking",
  "refines": "booking.uid"
}
```

`token` is the universal ABAG token. `resourceType` narrows broad resource
tokens when needed. `refines` is the concrete connector token that the app
action implementation understands. Bayesilisk can match typed tokens by the
abstract token and resource type, while the connector can still execute through
the concrete refinement.

Boundary rule: Bayesilisk matches typed-token dependencies using `token` plus
optional `resourceType`. It does not use `refines` to satisfy dependencies.
`refines` is only for connector execution and readable proposal output. Declare
typed tokens on the producing actions, consuming actions, required states, and
parameter bindings.

The same Cal.com-shaped sequence can therefore be written as:

```json
{
  "connectorActionGraph": {
    "actions": [
      {
        "actionId": "create-booking",
        "produces": [
          {"token": "resource.public_id", "resourceType": "booking", "refines": "booking.uid"},
          {"token": "resource.id", "resourceType": "booking", "refines": "booking.id"},
          {"token": "resource.public_id", "resourceType": "event_type", "refines": "eventType.slug"},
          {"token": "principal.actor", "resourceType": "calcom_user", "refines": "user.username"}
        ]
      },
      {
        "actionId": "cancel-booking",
        "requires": [
          {"token": "resource.id", "resourceType": "booking", "refines": "booking.id"}
        ],
        "produces": [
          {"token": "state.cancelled", "resourceType": "booking", "refines": "booking.status.cancelled"}
        ]
      },
      {
        "actionId": "open-public-booking-route",
        "requires": [
          {"token": "principal.actor", "resourceType": "calcom_user", "refines": "user.username"},
          {"token": "resource.public_id", "resourceType": "event_type", "refines": "eventType.slug"}
        ]
      }
    ],
    "sequenceRules": [
      {
        "ruleId": "cancelled-booking-public-replay",
        "invariantId": "calcom.cancelled_booking_replay_rejected",
        "expectedBehavior": {"status": 409},
        "requiresState": [
          {"token": "state.cancelled", "resourceType": "booking"}
        ],
        "goal": {
          "action": "open-public-booking-route",
          "paramBindings": {
            "rescheduleUid": {"token": "resource.public_id", "resourceType": "booking", "refines": "booking.uid"}
          }
        },
        "maxDepth": 4,
        "title": "Cancelled booking UID replay is rejected"
      }
    ]
  }
}
```

Universal ABAG tokens should come from a small vocabulary:

```text
principal.actor
session.authenticated
session.impersonated
scope.tenant
scope.owner
scope.foreign
resource.type
resource.id
resource.public_id
resource.private_id
resource.foreign_id
resource.stale_id
identifier.replay_token
identifier.single_use_token
identifier.invitation_token
identifier.reset_token
state.active
state.cancelled
state.deleted
state.expired
state.revoked
state.approved
state.rejected
boundary.public_route
boundary.private_route
boundary.api_route
boundary.ui_route
boundary.admin_route
capability.read
capability.write
capability.approve
capability.cancel
capability.export
capability.invite
capability.replay
evidence.status
evidence.redirect
evidence.rendered_state
evidence.network_response
```

Use app nouns only in `resourceType` and `refines`. The reusable unit is the
motif, for example:

```text
create resource -> transition lifecycle state -> replay old identifier across boundary
create privileged context -> downgrade/revoke privilege -> reuse stale session
create scoped object -> swap tenant/user id -> access through valid route
```

Bayesilisk will emit a `proposalKind: "workflow-sequence"` proposal such as:

```text
create-booking -> cancel-booking -> open-public-booking-route(rescheduleUid=booking.uid)
```

The connector receives that sequence, executes each declared action exactly,
and reports observed evidence. The connector must not decide pass/fail; it only
maps declared `actionId` values to real app fixture/browser/API actions and
returns concrete observations.

3. Execute real app behavior.

Use the app's own fixture helpers and browser/API test tools. A connector should
exercise real handlers or real UI paths, not mock the result it wants.

4. Write observed facts.

Set:

- `expectedStatus` from source-backed expected behavior;
- `observedStatus` from the actual browser/API response;
- `passed` from deterministic comparison;
- `failureDetail` from concrete evidence;
- `artifactPaths` for screenshots, traces, or logs when available.

5. Run Bayesilisk.

```sh
python3 -m bayesilisk \
  --seed 150 \
  --context /tmp/my-app-bayesilisk-context.json \
  --format markdown \
  --output /tmp/my-app-bayesilisk-report.md
```

For issue payloads:

```sh
python3 -m bayesilisk \
  --seed 150 \
  --context /tmp/my-app-bayesilisk-context.json \
  --issue-payloads \
  --output /tmp/my-app-bayesilisk-issues.json
```

## Action Mapping

Use stable connector action names internally. Example:

```json
{
  "open-resource-action": {
    "fixture": "createResourceWithOwner",
    "route": "/resource/{resourceId}/action?targetId={targetId}",
    "actor": "operator"
  }
}
```

In code, action names map to app behavior:

```ts
const action = proposal.connectorAction;

if (action === "open-resource-action") {
  const fixture = await createResourceWithOwner();
  const targetId = "missing-" + randomId();
  const response = await page.goto(`/resource/${fixture.resourceId}/action?targetId=${targetId}`);
  const observedStatus = response?.status() ?? 0;
  results.push({
    source: "microsoft-playwright",
    title: "Unknown target identifier must not open protected action",
    actorRole: "operator",
    invariantId: "myapp.unknown_target_id_rejected",
    route: "/resource/{resourceId}/action?targetId={targetId}",
    expectedStatus: 404,
    observedStatus,
    passed: observedStatus === 404,
    targetUrl: page.url(),
    failureDetail: observedStatus === 404 ? "" : "Unknown target ID was accepted.",
    artifactPaths: [],
    networkResponses: [{status: observedStatus, url: page.url()}],
    selector: "connector:open-resource-action",
    timestamp: new Date().toISOString()
  });
}
```

## LLM Team Rules

LLMs may help draft connector context:

- summarize nearby tests;
- extract route patterns;
- list parameters;
- identify likely fixture helpers;
- suggest connector action names.

LLMs must not:

- edit Bayesilisk core for an app connector;
- invent source evidence;
- invent observed statuses;
- set `passed` without executing the app;
- decide that a result is a bug after execution;
- open issues without Bayesilisk output and human/workflow approval.

## Coding Agent Contract

Coding agents should follow this sequence exactly:

```text
interview_connector_need
  -> establish_provenance
  -> connector_prompt_packet
  -> read local app tests/source
  -> write source context facts with explicit proposalRules/proposalGates
  -> scenario_plan or propose_probes
  -> run only app-specific connector actions against local fixtures
  -> write observed evidence facts
  -> verify_connector_outputs
  -> fix_packet only for verified ready findings
```

The older CLI-only path remains valid:

```text
read local app tests/source
write source context facts with explicit proposalRules/proposalGates
call python3 -m bayesilisk --probe-proposals-output
run only app-specific connector actions against local fixtures
write observed evidence facts
call python3 -m bayesilisk --context ... --issue-payloads
```

For Codex setup and MCP configuration, see {doc}`codex-mcp`.

The ingestible contract file is:

```text
examples/connector-agent-contract.json
```

## Human Review Checklist

Before running a connector against an app, confirm:

- the context references real files or tests;
- each expected status has a source-backed reason;
- every probe uses local/dev fixtures only;
- no production URLs or credentials are present;
- unsupported actions are reported, not silently passed;
- observed status comes from Playwright/API response data;
- the final issue-worthy result appears in Bayesilisk output.

## Good Connector Boundaries

Good:

```text
target-app/tests/bayesilisk/context-builder.ts
target-app/tests/bayesilisk/playwright-connector.spec.ts
target-app/tests/bayesilisk/actions.ts
```

Bad:

```text
bayesilisk/core/my_app_rules.py
bayesilisk/invariants_for_one_customer.py
```

The app owns app behavior. Bayesilisk consumes evidence and verifies the report.

## Worked Example

See [examples/calcom](https://github.com/sashakolpakov/bayesilisk/tree/main/examples/calcom)
for a real-app connector example.
It records the Cal.com repository URL, exact commit hash, connector source
contexts, Bayesilisk-generated route and workflow proposals, observed local
execution context, app-only reports, issue payloads, and upstream outcome
references. Those outcome references distinguish issue existence from stronger
human validation such as an upstream fix PR, human review approval, and
regression test linked to the Bayesilisk finding.
