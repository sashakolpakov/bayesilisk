# Bayesilisk

Bayesilisk is a deterministic local layer for permission, entitlement, route, and data-boundary sitting over Playwright, with Grassmann attention, and LLM-generated scenario-proposal workflows gated by a finite-state verifier.

It combines explicit rule invariants with Bayesian-style prioritization so tester and agent workflows can generate reproducible JSON, Markdown, and issue-ready findings.

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
- suggested issue title and body.

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

Context ingestion is separate from observation history and is designed for agent and issue-tracker context:

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

Bayesilisk scans the supplied context for fingerprints, issue/PR titles, agent notes, route/role terms, DMS/process terms, travel/expense terms, support-takeover terms, and related scenario language. Matching context nudges the relevant invariant priors but does not override rule failures. Existing fingerprints are treated as dedupe/mute signals so `bayesilisk.issue_payloads` does not create duplicate tracker issues.

## MCP tool server

Bayesilisk also has a local stdio MCP tool server:

```sh
bayesilisk-mcp
```

From a checkout, the module form is equivalent:

```sh
python3 -m bayesilisk.mcp_server
```

It exposes verifier tools:

- `bayesilisk.run`: run the full contextual report with optional observations and context.
- `bayesilisk.rank_context`: return the ranked failed probes from supplied agent, tracker, and repository context.
- `bayesilisk.issue_payloads`: return deduped issue payloads for failed findings marked `ready-for-issue`.
- `bayesilisk.propose_probes`: expand connector-supplied proposal rules and action graphs into probe proposals.

It also exposes Codex orchestration tools:

- `bayesilisk.interview_connector_need`;
- `bayesilisk.establish_provenance`;
- `bayesilisk.connector_prompt_packet`;
- `bayesilisk.scenario_plan`;
- `bayesilisk.verify_connector_outputs`;
- `bayesilisk.fix_packet`.

Agents should pass the current issue list, open PRs, branch facts, local verifier notes, and any known Bayesilisk fingerprints as context. The MCP tools still run locally, use deterministic seeds, and must not contact production systems or mutate issue trackers directly.

The MCP server prints an ASCII Bayesilisk logo and version to `stderr` on
startup. It keeps `stdout` reserved for framed MCP JSON-RPC messages. For Codex
configuration and connector onboarding, see {doc}`codex-mcp`.

## Microsoft Playwright bridge

Bayesilisk can be paired with Microsoft Playwright as an optional browser evidence collector. The browser probe is separate from the verifier: it opens a local or caller-provided target URL, clicks elements marked with `data-bayesilisk-probe`, records expected versus observed route status codes, and writes Bayesilisk context JSON.

Install the optional browser dependency and run the bundled target:

```sh
python3 -m pip install -e '.[playwright]'
python3 -m playwright install chromium
bayesilisk-demo
python3 tools/playwright_probe.py --demo --output /tmp/bayesilisk-playwright-context.json
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --format json
```

The target contract is intentionally small. Each probe row needs:

- `data-bayesilisk-probe`
- `data-title`
- `data-actor-role`
- `data-route`
- `data-invariant-id`
- `data-expected-status`
- a clickable child marked `data-run-probe`
- a status child marked `data-observed-status`

The `bayesilisk-demo` command serves a local brittle workflow app and prints the loop from browser evidence to issue payload. The older bundled `demo/playwright_target.html` remains a tiny static target for adapter tests. Generated context uses `agentNotes`, `repositoryFacts`, and explicit `priorAdjustments` to promote related Bayesilisk invariants, but it still does not prove a production defect by itself.

## Grassmann attention

Contextual reports also include a bounded Grassmann-style attention layer. It is modeled after the practical Cage pattern: extract local context-plane anchors, score overlap/coupling, and use that score to direct the next exploration step. Bayesilisk keeps the default implementation transparent and dependency-free by using an anchor-plane proxy. If `BAYESILISK_USE_OLLAMA_EMBEDDINGS=1` is set, it also calls Ollama `/api/embed` with `BAYESILISK_OLLAMA_MODEL` defaulting to `nomic-embed-text`, normalizes the returned vectors, and adds `embeddingSimilarity` as another plane signal.

The attention loop uses:

- Playwright `repositoryFacts`, especially expected versus observed route status;
- invariant ids and descriptions;
- route, role, module, tenant, DMS, HR, support, travel, and expense terms in context;
- prior adjustments supplied by the caller or inferred from context text;
- whether a plane has browser evidence, failures, or no coverage.

Each plane reports:

- `attentionScore`;
- `failureDensity`;
- `untestedness`;
- `sensitivity`;
- `playwrightEvidence`;
- `keywordHits`;
- `priorAdjustment`;
- `decayForFixedOrMuted` when a caller marks the invariant plane fixed, muted, or under regression watch;
- optional `embeddingSimilarity`;
- human-readable attention reasons.

High-attention planes are copied to `selectedPlaneIds`. The seeded generator uses those plane ids to add nearby generated scenarios, for example an HR/support plane can produce an expired-support HR document probe. This is the positive feedback loop: bad or under-tested planes receive more deterministic probes on the next report.

If `BAYESILISK_USE_OLLAMA_SCENARIO_MODEL=1` is set, Bayesilisk also runs a scenario proposer provider. The default provider is `ollama`, using Ollama `/api/chat`; the default model is `BAYESILISK_OLLAMA_SCENARIO_MODEL`, then `OLLAMA_MODEL`, then `gemma4:e2b`. `openai-compatible` is available for Chat Completions style endpoints. API keys are read from environment/config and are redacted from reports, issue bodies, and provenance. The prompt receives only selected planes plus the allowed fragment and invariant ids, and asks for strict JSON:

```json
{
  "scenarios": [
    {
      "title": "Support actor reaches HR documents after active takeover",
      "targetPlane": "hr.documents_customer_role_boundary",
      "fragments": ["role.support_takeover_active", "hr.payroll_file_route"],
      "invariants": ["support.takeover_session_required", "hr.documents_customer_role_boundary"]
    }
  ]
}
```

The proposal is accepted only if every fragment id and invariant id exists, the target plane is selected, and the target invariant is included in the scenario. Accepted proposals appear as `generated.model.*` scenarios. The current report contract still uses `generationBasis=weak-model-proposal:<plane>` and `weakModelScenarioGeneration.rejected` for compatibility with earlier Bayesilisk reports.

Accepted model-proposed findings include safe `modelProvenance`: provider name, model name, base URL or hostname class, prompt version, prompt hash, proposal hash, target plane, source context, and embedding model when embeddings were used. Reports never include API keys, raw secret headers, or full provider credentials.

The preferred local proposer for scenario generation is:

```sh
BAYESILISK_USE_OLLAMA_SCENARIO_MODEL=1 \
BAYESILISK_OLLAMA_SCENARIO_MODEL=gemma4:e2b \
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --format json
```

Scenario tests must cover both sides of each invariant. The deterministic catalog is expected to include at least one passing control and one failing bad-spot for every invariant before attention or model proposals are considered.

Attention never authorizes access, hides failures, or declares a bug. It only changes where Bayesilisk looks next. The final finding still separates:

- `attentionScore` and `attentionReasons`: selected by Grassmann-style attention;
- `generationBasis`: deterministic template, seeded composite, or model proposal provenance;
- `observedResult`: verified by deterministic invariants;
- `riskScore`: Bayesian-style prioritization after the invariant result.

## Hardening workflow

1. Run Bayesilisk with a fixed seed and a generated scenario count.
2. Open only `ready-for-issue` failed findings after checking they are not duplicates by fingerprint.
3. After a fix lands, add the fingerprint to `fixedFingerprints` and rerun the same seed.
4. Work through `regression-watch` and `harder-to-find-after-easy-breakages` modes before increasing the generated count.
5. Use new seeds for exploration only after the stable seed has no easy duplicate breakages.

## Boundaries

Bayesilisk is a verifier and prioritizer, not an authorization engine. It must not connect to production systems, inspect live customer data, create migrations, or emit internal platform claims as customer package claims.
