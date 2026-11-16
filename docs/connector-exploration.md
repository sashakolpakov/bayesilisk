# Model-Guided Connector Exploration

The connector proposer searches the **Abstract Bayesilisk Action Graph (ABAG)**
declared by the application. A model can choose alternative producers and compose
longer paths; it is not restricted to the built-in fragment catalog or to the
deterministic planner's first path.

```text
connector instructions + typed ABAG + goals + attention + retained procedures
  -> model proposes action/token sequences
  -> deterministic admission gate
  -> connector executes admitted sequences
  -> verification checks execution receipts and outcomes
  -> retain executed procedures and feed back coverage, outcomes and rejections
```

## Connector contract

Start with a source context containing `connectorActionGraph.actions` and
`sequenceRules`. The [Cal.com source context](https://github.com/sashakolpakov/bayesilisk/blob/main/examples/calcom/sequence-source-context.json)
is a worked example. Optional `connectorInstructions` describes fixture usage
and the application interface; `explorationFocus` directs attention.

Actions declare `requires` and `produces` typed tokens. The abstract key is
`token` plus optional `resourceType`; `refines` identifies a concrete handle used
by the connector. An action may declare `paramBindings` when it needs concrete
arguments during a sequence. A rule's `goal.paramBindings` supplies terminal
arguments without dropping other action-required arguments. A goal may specialize
an unqualified token type or select a declared concrete handle; it cannot change
the universal type or broaden an action's qualified type. Declare action bindings
too when a retained terminal action should be
reusable in the middle of a larger procedure. `initialTokens`, if supplied on
the graph, are available before the first action.

Each rule declares its invariant, terminal action, required state, expected
status, and `maxDepth`. The model chooses a path to that goal. Expectations and
concrete refinements remain contract-owned.
The prompt includes the complete ABAG and names initially executable actions.
Proposer capability is separate from admission: a weaker model may fail to
construct a valid path, and those failures remain explicit diagnostics.

The compact model response is:

```json
{
  "scenarios": [{
    "title": "Cancelled booking replay through a public route",
    "sequenceRuleId": "cancelled-booking-public-replay",
    "sequenceSteps": [
      {"connectorAction": "create-booking"},
      {"connectorAction": "cancel-booking"},
      {"connectorAction": "open-public-booking-route"}
    ]
  }]
}
```

The gate walks the proposed order without repairing it. It rejects unknown
actions/rules, missing or wrongly qualified tokens, unavailable parameter
bindings/refinements, missing goal states, wrong terminal actions, depth
violations, duplicates and attempted oracle/observation overrides. Admitted
output gets canonical token signatures, parameter mappings, a contract hash and
a stable proposal ID. Only this admitted output is sent for execution.

## Run with a local model

From the repository root, using models already installed in Ollama:

```sh
python3 -m bayesilisk connector propose examples/calcom/sequence-source-context.json \
  --enable-scenario-proposer --scenario-model qwen2.5-coder:3b \
  --enable-embeddings --embedding-model nomic-embed-text \
  --scenario-max-attempts 2 \
  --output proposals.json --plan-output scenario-plan.json
```

The ordinary output remains a proposal array for existing connectors. The plan
file includes the source contract, attention telemetry, model provenance and
admission diagnostics. An explicitly requested proposer failure exits nonzero;
it is not silently presented as successful model exploration. The model gets at
most `--scenario-max-attempts` calls (1–3), with deterministic rejection feedback
between attempts. `--scenario-proposal-limit`, `--limit` and each rule's
`maxDepth` bound the admitted work. Ollama receives a structured JSON response
schema; OpenAI-compatible providers receive JSON-object mode.

An existing OpenAI-compatible endpoint can be selected with
`--scenario-provider openai-compatible`, `--scenario-base-url`,
`--scenario-model` and `--scenario-api-key-env`. Credentials are resolved at
call time and excluded from plans and loop state.

For an external coding agent, save its response and use
`connector propose source.json --draft-plan model-scenarios.json
--plan-output scenario-plan.json`. Draft admission uses the same gate without a
provider call, even when generation is enabled in the environment. Combining a
draft with an explicit `--enable-scenario-proposer` is rejected; these are separate
operations. Draft provenance is labeled external and leaves its model unspecified.
MCP `propose_probes`
returns `proposalPrompt` as well as proposals and diagnostics; `scenario_plan`
now admits valid `draftPlan.scenarios` instead of merely inspecting them.

## Execute and verify

The connector executes each admitted `sequenceSteps` entry, resolves `params`
through its fixture state, and records the actual result. For planned workflow
sequences,
each observed fact must include its `proposalId` and ordered `executedActions`
receipt alongside the ordinary observed-context fields. An incomplete or
different sequence is rejected. The Cal.com connector example records these
fields; its application harness is still needed for actual Cal.com execution.

```sh
# Run your application-specific connector with proposals.json first.
python3 -m bayesilisk connector verify \
  --plan scenario-plan.json --observed observed-context.json
```

The saved source context is used when `--source` is omitted. Supply the current
source explicitly to check it against a potentially stale plan. Verification
revalidates every planned workflow against the source regardless of editable
origin labels, checks concrete bindings against a matching typed producer,
rechecks source-backed parameter probes, checks expected statuses
against the plan, and rejects missing or conflicting execution receipts. Saved
planning telemetry is carried into the report. Verification does not call the
model again or turn a proposed scenario into a finding.

## Retention and further exploration

```sh
python3 -m bayesilisk connector loop --state loop.json --source source-context.json \
  --enable-scenario-proposer --scenario-model qwen2.5-coder:3b
# Execute the returned proposals with your connector.
python3 -m bayesilisk connector loop --state loop.json --observed observed-context.json
```

Non-secret runtime options persist in the loop state. A sequence enters
`explorationMemory.retainedSequences` only after accepted observations match
its proposal ID and complete action receipt. Both passing tests and reproducible
failures can be useful executable procedures. A proposal that merely passes
structural validation is not promoted. Duplicate receipts do not increase its
execution count.

Later prompts include admitted procedures, prior execution outcomes and rejection
diagnostics. The model can compose a block with
`{"reuseProposalId": "sequence.model.…"}`. The gate rechecks the stored procedure,
expands the block and validates the whole new sequence. A changed graph or
`connectorVersion` invalidates retained entries. Set `connectorVersion` to the
revision of the executable mapping when that mapping changes.
An existing loop rejects a changed `--source`; start a fresh state file for the
new contract rather than silently retaining the previous plan and evidence.

The loop blocks rejected source contexts before handing off work. The loop
replans after execution; failed replanning exposes no executable proposal list.
A newly executed procedure counts as progress, even when no new failure is found.
It stops after bounded dry rounds or the round
cap; stopping is not a claim of complete coverage. The retained objects here are
executable ABAG sequences, with admission and replay records.

## Attention and interpretation

Connector attention uses the connector's invariants rather than demo-catalog
IDs. Each goal spans a subspace from its description, required states and typed
bindings. Modified Gram–Schmidt constructs an orthonormal basis; the geometric
term is the squared norm of the context vector's projection onto this subspace.
Coverage and observed failure density contribute separate bounded terms. The
result ranks candidate work and is included in the model's exploration prompt.

With `--enable-embeddings`, vectors come from the configured Ollama embedding
model. Otherwise deterministic hashed text features provide a local fallback;
embedding failures are visible in telemetry. This is a geometric routing method,
not evidence of a safety violation. Its benefit over coverage scheduling or
ordinary embedding similarity requires empirical comparison.

Admission establishes compliance with the declared graph and oracle contract.
Execution evidence still depends on the correctness of the connector's
instrumentation. ABAG's accumulated-token model does not establish every
intermediate application's semantics or object identity.

This interface admits test plans and checks recorded execution; it is not a live
tool-call controller. Runtime authority enforcement would additionally require
complete mediation of effectful calls, trusted state updates and independent
observations, including explicit revocation and consumption semantics.
