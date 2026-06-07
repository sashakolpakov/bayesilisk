# Closed Connector Loop

The closed loop drives a connector from nothing to verified findings with minimal
human babysitting, without ever crossing Bayesilisk's trust boundary.

Bayesilisk cannot run an arbitrary app — authentication, seed data, fixtures, and
the browser are app-specific — and it must never let a model decide the verdict.
So the loop is a **stateless next-step controller**: it performs every
*deterministic* step (scan → bind motifs → validate → verify → fix) and tracks
convergence, then returns the exact next action for the one step it cannot do —
writing and running the connector. The agent (Codex/Claude, or you) drives by
calling the controller repeatedly and passing the returned `state` back in.

## Phases

```text
              ┌─────────── start ───────────┐
   --spec/--source                          │
              ▼                              │
      scan → bind motifs → validate          │  (Bayesilisk, deterministic)
              ▼                              │
       await-connector ──────────────────────┘
              │   agent writes + runs the connector (the only manual step)
              ▼   --observed observed-context.json
           verify ──invalid──▶ blocked  (fix the observed facts, re-run)
              │ accepted
     new verified findings? ──yes──▶ repair  (apply fix briefs, re-execute)
              │ no
        dry round (+1)
              ▼
   maxDryRounds hit or maxRounds reached? ──yes──▶ converged
              │ no
       await-execution  (expand probes/fixtures, re-execute)
```

Convergence: the loop stops after `maxDryRounds` consecutive rounds with no new
verified ready-for-issue fingerprint (default 2), or when `maxRounds` is reached
(default 6), accumulating all verified findings and issue payloads. It is
deterministic — ids derive from content hashes and there are no clocks or RNG.

## CLI

```sh
# Step 1: scan a spec, bind motifs, and get the connector directive.
bayesilisk connector loop --state loop.json --spec openapi.json

# (write a connector, run it against local/dev/staging, capture observed-context.json)

# Step 2..N: feed observed evidence; the loop verifies, repairs, and converges.
bayesilisk connector loop --state loop.json --observed observed-context.json
```

Each call reads and rewrites `--state`, prints the current `phase` and
`nextAction`, and emits the step result (bound context, proposals, observation
validation, report, fix packet, accumulated issue payloads) as JSON. Start from a
hand-written source context with `--source` instead of `--spec`. Add `--pack` /
`--license` to include premium motifs, and `--max-rounds` / `--max-dry-rounds` to
tune convergence.

## MCP

The `connector_loop` tool is the same controller for agents: pass `state` (plus
`spec` / `sourceContext` / `observedContext`) and feed the returned `state` back
on the next call. See {doc}`motifs` for the motif library the loop binds and
{doc}`connectors` for the connector contract the agent fulfills during the execute
step.
