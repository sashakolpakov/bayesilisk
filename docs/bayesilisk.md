# Bayesilisk

Bayesilisk is a deterministic local verifier for permission, entitlement, route, and data-boundary scenarios. It combines explicit rule invariants with Bayesian-style prioritization so future issue worktrees can generate reproducible JSON or Markdown findings for Gitea issues.

Bayesilisk has no production access. It uses static scenario fragments from the repository, a caller-provided seed, and standard-library Python only.

## Layers

### Rule invariants

The rule layer pins invariants that should remain true across Travel, Expenses, Billing, HR, Support, DMS, and module-entitlement flows:

- Permission/role matrix: generated access patterns must use a route-allowed actor role.
- Roles: employee self-review is blocked; support access must have an active non-expired takeover session.
- Modules: expense approval and billing export routes must respect enabled customer modules.
- Routes: review, export, HR document, and support takeover routes are checked against the expected actor and entitlement.
- Data boundaries: DMS evidence must stay inside tenant and process boundaries; HR documents require customer HR/admin roles; travel itineraries cannot be silently inconsistent.
- Business scenario sequence: travel expenses require approved funding before expense submission or approval.
- Business scenario consistency: rental car, train, and airplane expenses must match chronological itinerary legs.

These rules are intentionally separate from probabilistic ranking. A failed invariant remains failed even if its score is lower than another finding.

### Bayesian prioritization

Each invariant carries a prior plus pass/fail likelihood weights. Bayesilisk updates the score for the observed result with:

```text
posterior = prior * likelihood / (prior * likelihood + (1 - prior) * (1 - likelihood))
```

The posterior is reported as `posteriorProbability` and `riskScore`, with a `posteriorMode` that separates highest fault-probability findings from harder-to-find modes. Easy breakages should be fixed or documented first; after a rerun with the same seed, `harder-to-find-after-easy-breakages` findings become the next priority. The score does not authorize access, change fixtures, or hide rule failures.

Bayesilisk can also read local observation history. Observation history can mark fingerprints as fixed, confirmed, or muted, and can adjust priors by invariant or scenario. This lets fixed easy breakages lose priority while still staying visible as regression watches, and lets confirmed local failures move upward without pretending that a production defect was proven.

### Scenario fragments

Fragments can be incomplete on their own and are composed into round-up scenarios. The default catalog includes:

- mundane cases, such as a finance actor exporting billing data with the billing module enabled;
- a travel funding request -> approval -> expenses flow with rental car, train, and airplane items;
- creative composed cases, such as expired support takeover plus foreign DMS evidence plus expense review;
- intentionally inconsistent cases, such as an impossible travel itinerary paired with employee self-review;
- air/train leg mismatch cases where expense dates or transport modes do not fit the itinerary.

This makes Bayesilisk useful for spotting cross-domain gaps before a full feature implementation exists.

## Generated composites

In addition to the fixed catalog, Bayesilisk uses a seeded composite generator. The generated scenarios draw role, module, route, funding, DMS, itinerary, and transport fragments into inhomogeneous round-up scenarios. Some generated scenarios are intentionally mundane; others mix support takeover, missing funding, disabled modules, foreign DMS evidence, rental car, train, and airplane items, or inconsistent itinerary dates. Generated fragments are still deterministic for a seed and are marked with `generatedScenario` and `generationBasis`.

## Report Contract

JSON and Markdown reports include:

- seed and tool version;
- scenario fragments, generated sub-scenarios, access patterns, and domains;
- stable finding fingerprint and dedupe key;
- expected invariant and invariant layer;
- observed result and observation detail;
- breakage/finding classification;
- issue readiness (`ready-for-issue`, `probe-only`, `regression-watch`, `no-issue-control`, or `do-not-open-muted`);
- observation basis and prior adjustment;
- prior, likelihood, posterior probability, posterior mode, and risk score;
- report sections for confirmed breakages, candidate probes, hard-to-find modes, and controls;
- suggested Gitea issue title and body.

Suggested issue bodies include the exact scenario id, fingerprint, issue readiness, classification, posterior mode, invariant expectation, observation, score, observation basis, access pattern, fragments, and reproduction command.

Only findings with `observedResult=fail` and `issueReadiness=ready-for-issue` should be opened automatically. `probe-only` findings need a local verifier or human confirmation first. `regression-watch` findings are prior fixed breakages that should stay visible but should not create duplicate issues by default.

## CLI

Run from the repository root:

```sh
python3 -m bayesilisk --seed 150 --format json --output /tmp/bayesilisk.json
python3 -m bayesilisk --seed 150 --format markdown --output /tmp/bayesilisk.md
python3 -m bayesilisk --seed 150 --format json --limit 3
python3 -m bayesilisk --seed 150 --format json --generated-count 16 --observations /tmp/bayesilisk-observations.json
python3 -m bayesilisk --seed 150 --format json --context /tmp/bayesilisk-context.json
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json --issue-payloads
```

The same seed and inputs produce byte-stable reports. Use a different seed to change scenario evaluation order before final risk sorting.

Observation history is optional JSON:

```json
{
  "source": "local-regression-log",
  "fixedFingerprints": ["bayesilisk:examplefixed0001"],
  "confirmedFingerprints": ["bayesilisk:examplebug00001"],
  "mutedFingerprints": ["bayesilisk:examplemuted001"],
  "priorAdjustments": {
    "travel.expense_items_match_itinerary": 0.08
  },
  "scenarioAdjustments": {
    "generated.01.finance.funding_missing.inconsistent_itinerary": 0.05
  }
}
```

Context ingestion is separate from observation history and is designed for agent and Gitea context:

```json
{
  "source": "develop-usa-loop",
  "agentNotes": [
    "Worker saw HR documents process metadata, DMS tenant scope, and support takeover access risks."
  ],
  "issues": [
    {
      "number": 8,
      "state": "open",
      "title": "[USA] Add HR documents process-context filter and metadata display",
      "body": "DMS process context and HR document metadata display"
    }
  ],
  "pullRequests": [
    {
      "number": 170,
      "state": "open",
      "title": "[USA] Review Bayesilisk verifier hardening"
    }
  ],
  "mutedFingerprints": ["bayesilisk:examplemuted001"]
}
```

Bayesilisk scans the supplied context for fingerprints, issue/PR titles, agent notes, route/role terms, DMS/process terms, travel/expense terms, support-takeover terms, and related scenario language. Matching context nudges the relevant invariant priors but does not override rule failures. Existing fingerprints are treated as dedupe/mute signals so `bayesilisk.issue_payloads` does not create duplicate Gitea issues.

## MCP tool server

Bayesilisk also has a small stdio MCP tool server:

```sh
python3 -m bayesilisk.mcp_server
```

It exposes three tools:

- `bayesilisk.run`: run the full contextual report with optional observations and context.
- `bayesilisk.rank_context`: return the ranked failed probes from supplied agent/Gitea/repo context.
- `bayesilisk.issue_payloads`: return deduped Gitea-ready issue payloads for failed findings marked `ready-for-issue`.

Agents should pass the current issue list, open PRs, branch facts, local verifier notes, and any known Bayesilisk fingerprints as context. The MCP tools still run locally, use deterministic seeds, and must not contact production systems or mutate Gitea directly.

## Hardening workflow

1. Run Bayesilisk with a fixed seed and a generated scenario count.
2. Open only `ready-for-issue` failed findings after checking they are not duplicates by fingerprint.
3. After a fix lands, add the fingerprint to `fixedFingerprints` and rerun the same seed.
4. Work through `regression-watch` and `harder-to-find-after-easy-breakages` modes before increasing the generated count.
5. Use new seeds for exploration only after the stable seed has no easy duplicate breakages.

## Boundaries

Bayesilisk is a verifier and prioritizer, not an authorization engine. It must not connect to production systems, inspect live customer data, create migrations, or emit internal platform claims as customer package claims.
