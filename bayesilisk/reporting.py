from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from .attention import grassmann_attention
from .catalog import FRAGMENTS, SCENARIOS, generated_composite_scenarios
from .config import effective_runtime_config, report_runtime_config
from .constants import ROLE_ROUTE_MATRIX, VERSION
from .context import _context_items, _dict_or_empty, context_observations, context_summary, merge_observations, observation_basis
from .facts import (
    access_pattern,
    finding_fingerprint,
    merge_facts,
    minimize_failing_generated_scenario,
    scenario_fragment_payload,
    scenario_reproducer_payload,
    sub_scenarios,
)
from .invariants import INVARIANTS, bayesian_posterior, clamp_probability, finding_classification, issue_readiness, posterior_mode
from .model_proposals import weak_model_scenarios
from .types import Fragment, Invariant, Scenario

def report_sections(findings: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {
        "confirmedBreakages": [
            finding["fingerprint"]
            for finding in findings
            if finding["observedResult"] == "fail" and finding["issueReadiness"] == "ready-for-issue"
        ],
        "candidateProbes": [
            finding["fingerprint"]
            for finding in findings
            if finding["observedResult"] == "fail" and finding["issueReadiness"] in {"probe-only", "regression-watch"}
        ],
        "hardToFindModes": [
            finding["fingerprint"]
            for finding in findings
            if finding["posteriorMode"] == "harder-to-find-after-easy-breakages"
            or finding["classification"] == "breakage.hard-to-find"
        ],
        "controls": [
            finding["fingerprint"]
            for finding in findings
            if finding["observedResult"] == "pass"
        ],
    }


def build_report(
    seed: int,
    limit: int | None = None,
    generated_count: int = 8,
    observations: dict[str, Any] | None = None,
    grassmann: dict[str, Any] | None = None,
    model_scenarios: list[Scenario] | None = None,
    runtime_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    observations = _dict_or_empty(observations)
    grassmann = _dict_or_empty(grassmann)
    effective_config = effective_runtime_config(runtime_config)
    attention_by_invariant = {
        plane["invariantId"]: plane
        for plane in grassmann.get("planes", [])
        if isinstance(plane, dict) and isinstance(plane.get("invariantId"), str)
    }
    model_provenance_by_scenario = {
        scenario.id: scenario.provenance
        for scenario in model_scenarios or []
        if isinstance(scenario.provenance, dict) and scenario.provenance
    }
    rng = random.Random(seed)
    fragment_by_id = {fragment.id: fragment for fragment in FRAGMENTS}
    invariant_by_id = {invariant.id: invariant for invariant in INVARIANTS}
    generated_scenarios = generated_composite_scenarios(
        seed,
        generated_count,
        attention_plane_ids=grassmann.get("selectedPlaneIds", []),
        model_scenarios=model_scenarios,
    )
    scenario_order = [*SCENARIOS, *generated_scenarios]
    rng.shuffle(scenario_order)

    findings: list[dict[str, Any]] = []
    for scenario in scenario_order:
        fragments = [fragment_by_id[fragment_id] for fragment_id in scenario.fragment_ids]
        facts = merge_facts(fragments)
        pattern = access_pattern(facts)
        entries = sub_scenarios(fragments)
        for invariant_id in scenario.invariant_ids:
            invariant = invariant_by_id[invariant_id]
            passed, observation = invariant.evaluator(facts)
            likelihood = invariant.pass_likelihood if passed else invariant.fail_likelihood
            fingerprint = finding_fingerprint(scenario, invariant, fragments)
            basis = observation_basis(fingerprint, scenario, invariant, observations)
            adjusted_prior = clamp_probability(invariant.prior + basis["priorDelta"])
            risk_score = bayesian_posterior(adjusted_prior, likelihood)
            observed_result = "pass" if passed else "fail"
            classification = finding_classification(passed, risk_score, invariant)
            mode = posterior_mode(passed, risk_score, invariant)
            readiness = issue_readiness(passed, classification, basis)
            title = suggested_title(scenario, invariant, observed_result, classification)
            attention_plane = attention_by_invariant.get(invariant.id, {})
            model_provenance = model_provenance_by_scenario.get(scenario.id)
            original_scenario = scenario_reproducer_payload(scenario, fragments, observation=observation)
            minimized_reproducer = None
            if not passed:
                minimized_reproducer = minimize_failing_generated_scenario(
                    scenario,
                    invariant,
                    fragments,
                    observation,
                )
            body = suggested_body(
                scenario,
                invariant,
                fragments,
                observation,
                risk_score,
                classification,
                mode,
                pattern,
                fingerprint,
                readiness,
                basis,
                original_scenario=original_scenario if minimized_reproducer else None,
                minimized_reproducer=minimized_reproducer,
            )
            findings.append(
                {
                    "id": f"{scenario.id}:{invariant.id}",
                    "fingerprint": fingerprint,
                    "dedupeKey": f"{fingerprint}:{invariant.id}",
                    "scenarioId": scenario.id,
                    "scenarioTitle": scenario.title,
                    "scenarioTone": scenario.tone,
                    "generatedScenario": scenario.generated,
                    "generationBasis": scenario.generation_basis,
                    "modelProvenance": model_provenance,
                    "originalScenario": original_scenario if minimized_reproducer else None,
                    "minimizedReproducer": minimized_reproducer,
                    "subScenarios": entries,
                    "fragments": scenario_fragment_payload(fragments),
                    "accessPattern": pattern,
                    "expectedInvariant": invariant.expected,
                    "invariantId": invariant.id,
                    "invariantLayer": invariant.layer,
                    "observedResult": observed_result,
                    "observation": observation,
                    "classification": classification,
                    "issueReadiness": readiness,
                    "attentionScore": attention_plane.get("attentionScore", 0.0),
                    "attentionReasons": attention_plane.get("reasons", ["no-grassmann-attention"]),
                    "observationBasis": basis,
                    "prior": invariant.prior,
                    "adjustedPrior": adjusted_prior,
                    "likelihood": likelihood,
                    "posteriorProbability": risk_score,
                    "posteriorMode": mode,
                    "riskScore": risk_score,
                    "suggestedIssueTitle": title,
                    "suggestedIssueBody": body,
                }
            )

    findings.sort(key=lambda item: (-item["riskScore"], item["posteriorMode"], item["id"]))
    if limit is not None:
        findings = findings[:limit]
    sections = report_sections(findings)
    verified_ledger = [
        {
            "classification": finding["classification"],
            "fingerprint": finding["fingerprint"],
            "invariantId": finding["invariantId"],
            "issueReadiness": finding["issueReadiness"],
            "observedResult": finding["observedResult"],
            "riskScore": finding["riskScore"],
            "scenarioId": finding["scenarioId"],
        }
        for finding in findings
    ]
    return {
        "tool": VERSION,
        "seed": seed,
        "deterministic": True,
        "productionAccess": False,
        "generatedScenarioCount": len(generated_scenarios),
        "effectiveConfiguration": report_runtime_config(effective_config),
        "grassmannAttention": grassmann or {
            "boundedFeedback": True,
            "embeddingMode": "disabled",
            "planes": [],
            "selectedPlaneIds": [],
            "source": "none",
        },
        "weakModelScenarioGeneration": grassmann.get("weakModelScenarioGeneration", {"enabled": False})
        if grassmann
        else {"enabled": False},
        "observedByPlaywright": [],
        "selectedByGrassmannAttention": [
            {
                "attentionScore": plane.get("attentionScore", 0.0),
                "invariantId": plane.get("invariantId"),
                "reasons": plane.get("reasons", []),
            }
            for plane in grassmann.get("planes", [])
            if plane.get("invariantId") in set(grassmann.get("selectedPlaneIds", []))
        ],
        "proposedByModel": [],
        "verifiedByBayesilisk": verified_ledger,
        "domains": ["Travel", "Expenses", "Billing", "HR", "Support", "DMS", "module entitlements"],
        "prioritizationPolicy": (
            "Sort by posterior fault probability first. Fix or document breakage.easy findings, rerun with the "
            "same seed, then promote harder-to-find-after-easy-breakages modes."
        ),
        "invariants": [
            {
                "difficulty": invariant.difficulty,
                "expected": invariant.expected,
                "failLikelihood": invariant.fail_likelihood,
                "id": invariant.id,
                "layer": invariant.layer,
                "passLikelihood": invariant.pass_likelihood,
                "prior": invariant.prior,
            }
            for invariant in INVARIANTS
        ],
        "roleRouteMatrix": {route: sorted(roles) for route, roles in ROLE_ROUTE_MATRIX.items()},
        "sections": sections,
        "findings": findings,
    }


def build_contextual_report(
    seed: int,
    limit: int | None = None,
    generated_count: int = 8,
    observations: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
    runtime_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = _dict_or_empty(context)
    observations = _dict_or_empty(observations)
    effective_config = effective_runtime_config(runtime_config)
    summary = context_summary(context)
    merged_observations = merge_observations(observations, context_observations(context))
    attention = grassmann_attention(context, observations, runtime_config=effective_config)
    model_scenarios, model_generation = weak_model_scenarios(attention, runtime_config=effective_config)
    attention["weakModelScenarioGeneration"] = model_generation
    report = build_report(
        seed,
        limit=limit,
        generated_count=generated_count,
        observations=merged_observations,
        grassmann=attention,
        model_scenarios=model_scenarios,
        runtime_config=effective_config,
    )
    report["contextSummary"] = summary
    report["contextObservationSource"] = merged_observations.get("source", "none")
    report["observedByPlaywright"] = [
        {
            "actorRole": fact.get("actorRole"),
            "expectedStatus": fact.get("expectedStatus"),
            "invariantId": fact.get("invariantId"),
            "observedStatus": fact.get("observedStatus"),
            "passed": fact.get("passed"),
            "route": fact.get("route"),
            "source": fact.get("source"),
            "title": fact.get("title"),
        }
        for fact in context.get("repositoryFacts", [])
        if isinstance(fact, dict) and fact.get("source") == "microsoft-playwright"
    ]
    report["selectedByGrassmannAttention"] = [
        {
            "attentionScore": plane.get("attentionScore", 0.0),
            "invariantId": plane.get("invariantId"),
            "reasons": plane.get("reasons", []),
        }
        for plane in attention.get("planes", [])
        if plane.get("invariantId") in set(attention.get("selectedPlaneIds", []))
    ]
    report["proposedByModel"] = {
        "acceptedCount": model_generation.get("acceptedCount", 0),
        "enabled": model_generation.get("enabled", False),
        "provider": model_generation.get("source", "disabled"),
        "rejectedCount": model_generation.get("rejectedCount", 0),
    }
    report["rankedProbes"] = ranked_probes(report, limit=limit)
    report["issuePayloads"] = issue_payloads(report, context=context, limit=limit)
    return report


def ranked_probes(report: dict[str, Any], limit: int | None = None) -> list[dict[str, Any]]:
    probes = [
        {
            "accessPattern": finding["accessPattern"],
            "classification": finding["classification"],
            "fingerprint": finding["fingerprint"],
            "generatedScenario": finding["generatedScenario"],
            "invariantId": finding["invariantId"],
            "issueReadiness": finding["issueReadiness"],
            "observedResult": finding["observedResult"],
            "posteriorMode": finding["posteriorMode"],
            "reproduce": (
                f"python3 -m bayesilisk --seed {report['seed']} "
                f"--generated-count {report['generatedScenarioCount']} --format json"
            ),
            "riskScore": finding["riskScore"],
            "scenarioId": finding["scenarioId"],
            "scenarioTitle": finding["scenarioTitle"],
            "title": finding["suggestedIssueTitle"],
        }
        for finding in report["findings"]
        if finding["observedResult"] == "fail"
    ]
    if limit is not None:
        return probes[:limit]
    return probes


def _existing_context_titles(context: dict[str, Any] | None) -> set[str]:
    titles: set[str] = set()
    if not context:
        return titles
    for item in _context_items(context):
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        if isinstance(title, str):
            titles.add(title.strip().lower())
    return titles


def issue_payloads(
    report: dict[str, Any],
    context: dict[str, Any] | None = None,
    limit: int | None = None,
    include_existing: bool = False,
) -> list[dict[str, Any]]:
    existing_fingerprints = set(context_summary(context)["fingerprints"])
    existing_titles = _existing_context_titles(context)
    payloads: list[dict[str, Any]] = []
    for finding in report["findings"]:
        if finding["observedResult"] != "fail" or finding["issueReadiness"] != "ready-for-issue":
            continue
        title = finding["suggestedIssueTitle"]
        title_key = title.strip().lower()
        dedupe_state = "new"
        if finding["fingerprint"] in existing_fingerprints:
            dedupe_state = "existing-fingerprint"
        elif title_key in existing_titles:
            dedupe_state = "existing-title"
        if dedupe_state != "new" and not include_existing:
            continue
        labels = ["bayesilisk", "usa"]
        if finding["generatedScenario"]:
            labels.append("generated-scenario")
        payloads.append(
            {
                "body": finding["suggestedIssueBody"],
                "classification": finding["classification"],
                "dedupeKey": finding["dedupeKey"],
                "dedupeState": dedupe_state,
                "fingerprint": finding["fingerprint"],
                "invariantId": finding["invariantId"],
                "issueReadiness": finding["issueReadiness"],
                "issuePayloadSource": "verifiedByBayesilisk",
                "labels": labels,
                "attentionReasons": finding.get("attentionReasons", []),
                "attentionScore": finding.get("attentionScore", 0.0),
                "minimizedReproducer": finding.get("minimizedReproducer"),
                "modelProvenance": finding.get("modelProvenance"),
                "originalScenario": finding.get("originalScenario"),
                "posteriorMode": finding["posteriorMode"],
                "riskScore": finding["riskScore"],
                "scenarioId": finding["scenarioId"],
                "title": title,
            }
        )
        if limit is not None and len(payloads) >= limit:
            break
    return payloads


def suggested_title(
    scenario: Scenario,
    invariant: Invariant,
    observed_result: str,
    classification: str,
) -> str:
    if observed_result == "fail":
        return f"Bayesilisk {classification}: {scenario.tone} scenario violates {invariant.id}"
    return f"Bayesilisk {classification}: {scenario.tone} scenario confirms {invariant.id}"


def suggested_body(
    scenario: Scenario,
    invariant: Invariant,
    fragments: list[Fragment],
    observation: str,
    risk_score: float,
    classification: str,
    mode: str,
    pattern: dict[str, Any],
    fingerprint: str,
    readiness: str,
    basis: dict[str, Any],
    original_scenario: dict[str, Any] | None = None,
    minimized_reproducer: dict[str, Any] | None = None,
) -> str:
    fragment_lines = "\n".join(f"- `{fragment.id}` ({fragment.domain}): {fragment.summary}" for fragment in fragments)
    pattern_json = json.dumps(pattern, indent=2, sort_keys=True)
    basis_json = json.dumps(basis, indent=2, sort_keys=True)
    minimization_section = ""
    if original_scenario and minimized_reproducer:
        original_json = json.dumps(
            {
                "accessPattern": original_scenario["accessPattern"],
                "fragmentIds": original_scenario["fragmentIds"],
                "observation": original_scenario.get("observation"),
            },
            indent=2,
            sort_keys=True,
        )
        minimized_json = json.dumps(
            {
                "accessPattern": minimized_reproducer["accessPattern"],
                "fragmentIds": minimized_reproducer["fragmentIds"],
                "observation": minimized_reproducer["observation"],
                "removedFragmentIds": minimized_reproducer["removedFragmentIds"],
            },
            indent=2,
            sort_keys=True,
        )
        minimization_section = (
            "Original generated scenario:\n"
            f"```json\n{original_json}\n```\n\n"
            "Minimized reproducer:\n"
            f"```json\n{minimized_json}\n```\n\n"
        )
    return (
        f"Scenario `{scenario.id}`: {scenario.title}\n\n"
        f"Fingerprint: `{fingerprint}`\n\n"
        f"Classification: `{classification}`\n\n"
        f"Issue readiness: `{readiness}`\n\n"
        f"Posterior mode: `{mode}`\n\n"
        f"Expected invariant: {invariant.expected}\n\n"
        f"Observed: {observation}\n\n"
        f"Risk score: {risk_score:.6f}\n\n"
        f"Observation basis:\n```json\n{basis_json}\n```\n\n"
        f"Access pattern:\n```json\n{pattern_json}\n```\n\n"
        f"{minimization_section}"
        f"Fragments:\n{fragment_lines}\n\n"
        "Reproduce with `python3 -m bayesilisk --seed <seed> --format json`."
    )


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Bayesilisk Report",
        "",
        f"- Tool: `{report['tool']}`",
        f"- Seed: `{report['seed']}`",
        f"- Deterministic: `{str(report['deterministic']).lower()}`",
        f"- Production access: `{str(report['productionAccess']).lower()}`",
        f"- Generated scenarios: `{report['generatedScenarioCount']}`",
        f"- Grassmann attention: `{report['grassmannAttention']['embeddingMode']}`",
        f"- Prioritization: {report['prioritizationPolicy']}",
        "",
        "## Sections",
        "",
        f"- Confirmed breakages: `{len(report['sections']['confirmedBreakages'])}`",
        f"- Candidate probes: `{len(report['sections']['candidateProbes'])}`",
        f"- Hard-to-find modes: `{len(report['sections']['hardToFindModes'])}`",
        f"- Controls: `{len(report['sections']['controls'])}`",
        "",
        "## Findings",
        "",
    ]
    for finding in report["findings"]:
        lines.extend(
            [
                f"### {finding['suggestedIssueTitle']}",
                "",
                f"- Scenario: `{finding['scenarioId']}` ({finding['scenarioTone']})",
                f"- Fingerprint: `{finding['fingerprint']}`",
                f"- Generated scenario: `{str(finding['generatedScenario']).lower()}`",
                f"- Classification: `{finding['classification']}`",
                f"- Issue readiness: `{finding['issueReadiness']}`",
                f"- Posterior mode: `{finding['posteriorMode']}`",
                f"- Expected invariant: {finding['expectedInvariant']}",
                f"- Observed result: `{finding['observedResult']}`",
                f"- Observation: {finding['observation']}",
                f"- Observation basis: `{', '.join(finding['observationBasis']['tags'])}`",
                f"- Attention score: `{finding.get('attentionScore', 0.0):.6f}`",
                f"- Attention reasons: `{', '.join(finding.get('attentionReasons', []))}`",
                f"- Risk score: `{finding['riskScore']:.6f}`",
                "- Sub-scenarios:",
            ]
        )
        for entry in finding["subScenarios"]:
            complete = str(entry["completeAlone"]).lower()
            lines.append(f"  - `{entry['fragmentId']}` [{entry['domain']}], complete alone: `{complete}`")
        lines.extend(
            [
                "- Access pattern:",
                "```json",
                json.dumps(finding["accessPattern"], indent=2, sort_keys=True),
                "```",
                "",
                "Suggested issue body:",
                "",
                "````markdown",
                finding["suggestedIssueBody"],
                "````",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_output(content: str, output_path: Path | None) -> None:
    if output_path is None:
        print(content, end="")
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
