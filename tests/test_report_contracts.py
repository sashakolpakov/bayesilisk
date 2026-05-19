from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class SchemaError(AssertionError):
    pass


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_registry() -> dict[str, dict[str, Any]]:
    return {path.name: load_json(path) for path in SCHEMA_DIR.glob("*.schema.json")}


def canonical_report(report: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(report, sort_keys=True))
    for finding in payload.get("findings", []):
        finding.pop("minimizedReproducer", None)
        finding.pop("originalScenario", None)
    for issue_payload in payload.get("issuePayloads", []):
        issue_payload.pop("minimizedReproducer", None)
        issue_payload.pop("originalScenario", None)
    return payload


def validate_schema(instance: Any, schema: dict[str, Any], *, registry: dict[str, dict[str, Any]], path: str = "$") -> None:
    ref = schema.get("$ref")
    if ref:
        target = registry[ref]
        validate_schema(instance, target, registry=registry, path=path)
        return

    if "const" in schema and instance != schema["const"]:
        raise SchemaError(f"{path}: expected const {schema['const']!r}, got {instance!r}")
    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaError(f"{path}: expected one of {schema['enum']!r}, got {instance!r}")

    schema_type = schema.get("type")
    if schema_type is not None and not type_matches(instance, schema_type):
        raise SchemaError(f"{path}: expected type {schema_type!r}, got {type(instance).__name__}")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        missing = [key for key in required if key not in instance]
        if missing:
            raise SchemaError(f"{path}: missing required keys {missing!r}")

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        if additional is False:
            extra = sorted(set(instance) - set(properties))
            if extra:
                raise SchemaError(f"{path}: unexpected keys {extra!r}")
        elif isinstance(additional, dict):
            for key in sorted(set(instance) - set(properties)):
                validate_schema(instance[key], additional, registry=registry, path=f"{path}.{key}")
        for key, subschema in properties.items():
            if key in instance:
                validate_schema(instance[key], subschema, registry=registry, path=f"{path}.{key}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            raise SchemaError(f"{path}: expected at least {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            raise SchemaError(f"{path}: expected at most {schema['maxItems']} items")
        if schema.get("uniqueItems") and len(instance) != len({json.dumps(item, sort_keys=True) for item in instance}):
            raise SchemaError(f"{path}: expected unique items")
        if "items" in schema:
            for index, item in enumerate(instance):
                validate_schema(item, schema["items"], registry=registry, path=f"{path}[{index}]")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise SchemaError(f"{path}: expected minimum length {schema['minLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            raise SchemaError(f"{path}: expected pattern {schema['pattern']!r}, got {instance!r}")

    if isinstance(instance, int | float) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            raise SchemaError(f"{path}: expected >= {schema['minimum']}, got {instance}")
        if "maximum" in schema and instance > schema["maximum"]:
            raise SchemaError(f"{path}: expected <= {schema['maximum']}, got {instance}")


def type_matches(instance: Any, schema_type: str | list[str]) -> bool:
    if isinstance(schema_type, list):
        return any(type_matches(instance, item) for item in schema_type)
    if schema_type == "array":
        return isinstance(instance, list)
    if schema_type == "boolean":
        return isinstance(instance, bool)
    if schema_type == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if schema_type == "null":
        return instance is None
    if schema_type == "number":
        return isinstance(instance, int | float) and not isinstance(instance, bool)
    if schema_type == "object":
        return isinstance(instance, dict)
    if schema_type == "string":
        return isinstance(instance, str)
    raise SchemaError(f"unsupported schema type {schema_type!r}")


def calcom_typed_action_graph_context() -> dict[str, Any]:
    return {
        "source": "connector-source-context",
        "agentNotes": ["connector exposes ABAG typed tokens"],
        "priorAdjustments": {},
        "repositoryFacts": [],
        "connectorActionGraph": {
            "actions": [
                {
                    "actionId": "create-booking",
                    "produces": [
                        {"token": "resource.public_id", "resourceType": "booking", "refines": "booking.uid"},
                        {"token": "resource.id", "resourceType": "booking", "refines": "booking.id"},
                        {"token": "resource.public_id", "resourceType": "event_type", "refines": "eventType.slug"},
                        {"token": "principal.actor", "resourceType": "calcom_user", "refines": "user.username"},
                    ],
                },
                {
                    "actionId": "cancel-booking",
                    "requires": [
                        {"token": "resource.id", "resourceType": "booking", "refines": "booking.id"},
                    ],
                    "produces": [
                        {"token": "state.cancelled", "resourceType": "booking", "refines": "booking.status.cancelled"},
                    ],
                },
                {
                    "actionId": "open-public-booking-route",
                    "requires": [
                        {"token": "principal.actor", "resourceType": "calcom_user", "refines": "user.username"},
                        {"token": "resource.public_id", "resourceType": "event_type", "refines": "eventType.slug"},
                    ],
                },
            ],
            "sequenceRules": [
                {
                    "ruleId": "cancelled-booking-replay",
                    "expectedBehavior": {"status": 409},
                    "goal": {
                        "action": "open-public-booking-route",
                        "paramBindings": {
                            "rescheduleUid": {
                                "token": "resource.public_id",
                                "resourceType": "booking",
                                "refines": "booking.uid",
                            }
                        },
                    },
                    "invariantId": "external.cancelled_booking_replay_rejected",
                    "maxDepth": 4,
                    "requiresState": [
                        {"token": "state.cancelled", "resourceType": "booking"},
                    ],
                    "title": "Cancelled booking UID replay is rejected",
                }
            ],
        },
        "playwrightProbe": {"artifactCount": 0, "failedCount": 0, "passedCount": 0, "resultCount": 0, "target": None},
    }


def test_golden_baseline_report_matches_report_schema(monkeypatch: Any) -> None:
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "0")
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_EMBEDDINGS", "0")
    from bayesilisk import reporting

    registry = schema_registry()
    golden = load_json(FIXTURE_DIR / "baseline_report.json")
    current = reporting.build_report(150)

    validate_schema(golden, registry["report.schema.json"], registry=registry)
    validate_schema(current, registry["report.schema.json"], registry=registry)
    assert canonical_report(current) == golden


def test_golden_playwright_context_report_matches_schemas(monkeypatch: Any) -> None:
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "0")
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_EMBEDDINGS", "0")
    from bayesilisk import reporting

    registry = schema_registry()
    context = load_json(FIXTURE_DIR / "playwright_context.json")
    golden = load_json(FIXTURE_DIR / "playwright_context_report.json")
    current = reporting.build_contextual_report(150, context=context)

    validate_schema(context, registry["playwright-context.schema.json"], registry=registry)
    validate_schema(golden, registry["report.schema.json"], registry=registry)
    validate_schema(current, registry["report.schema.json"], registry=registry)
    assert canonical_report(current) == golden


def test_abag_example_context_matches_schema_and_generates_sequence() -> None:
    from bayesilisk.probe_proposals import generate_sequence_proposals

    registry = schema_registry()
    context = load_json(REPO_ROOT / "examples" / "abag-action-graph-context.json")

    validate_schema(context, registry["playwright-context.schema.json"], registry=registry)
    proposals = generate_sequence_proposals(context)

    assert len(proposals) == 1
    proposal = proposals[0]
    assert proposal["proposalKind"] == "workflow-sequence"
    assert [step["connectorAction"] for step in proposal["sequenceSteps"]] == [
        "create-invite",
        "revoke-invite",
        "accept-invite-route",
    ]
    assert proposal["sequenceSteps"][-1]["params"] == {"inviteToken": "invite.token"}


def test_current_issue_payloads_match_schema() -> None:
    from bayesilisk import reporting

    registry = schema_registry()
    report = reporting.build_report(150)
    payloads = reporting.issue_payloads(report)

    assert payloads
    for payload in payloads:
        validate_schema(payload, registry["issue-payload.schema.json"], registry=registry)


def test_external_connector_context_mismatch_becomes_verified_finding(monkeypatch: Any) -> None:
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "0")
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_EMBEDDINGS", "0")
    from bayesilisk import reporting

    registry = schema_registry()
    context = {
        "source": "external-app-connector",
        "repositoryFacts": [
            {
                "actorRole": "operator",
                "artifactPaths": ["/tmp/external-proof.png"],
                "expectedStatus": 403,
                "failureDetail": "Unknown target identifier was ignored and the protected action was visible.",
                "invariantId": "external.unknown_target_id_rejected",
                "observedStatus": 200,
                "passed": False,
                "route": "/resource/{resourceId}/action?targetId={unknownTargetId}",
                "source": "connector-observation",
                "targetUrl": "http://localhost:3000/resource/123/action?targetId=missing",
                "title": "Unknown target identifier must not open protected action",
            }
        ],
    }

    report = reporting.build_contextual_report(150, context=context)
    finding = next(
        item
        for item in report["findings"]
        if item["invariantId"] == "external.unknown_target_id_rejected"
    )

    validate_schema(report, registry["report.schema.json"], registry=registry)
    assert finding["classification"] == "breakage.context-observed"
    assert finding["issueReadiness"] == "ready-for-issue"
    assert finding["observedResult"] == "fail"
    assert finding["attentionReasons"] == ["connector-evidence", "external-context-failure"]
    assert any(
        payload["fingerprint"] == finding["fingerprint"]
        and payload["issuePayloadSource"] == "verifiedByBayesilisk"
        for payload in report["issuePayloads"]
    )


def test_source_context_generates_connector_probe_proposals(monkeypatch: Any) -> None:
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "0")
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_EMBEDDINGS", "0")
    from bayesilisk.probe_proposals import generate_probe_proposals
    from bayesilisk import reporting

    context = {
        "source": "connector-source-context",
        "agentNotes": ["source scan found route params that can be mutated"],
        "priorAdjustments": {},
        "repositoryFacts": [
            {
                "availableActions": ["open-resource-action"],
                "expectedBehavior": {"description": "Connector-owned rule must hold.", "status": 418},
                "invariantId": "external.connector_owned_rule",
                "nearbyTests": ["valid target opens the action"],
                "params": [
                    {"kind": "id", "location": "path", "name": "resourceId", "required": True},
                    {"kind": "id", "location": "query", "name": "targetId", "required": True},
                ],
                "path": "app/routes/resource.ts",
                "proposalRules": {
                    "targetId": [
                        {"id": "connector-rule-a", "value": "connector-value-a"},
                        {"id": "connector-rule-b", "value": "connector-value-b"},
                    ]
                },
                "routePattern": "/resource/{resourceId}/action?targetId={targetId}",
                "source": "repository-scan",
                "sourceText": "TODO: force 404 when targetId is not found.",
                "title": "Resource action validates target identifier",
            }
        ],
        "playwrightProbe": {"artifactCount": 0, "failedCount": 0, "passedCount": 0, "resultCount": 0, "target": None},
    }

    proposals = generate_probe_proposals(context)
    report = reporting.build_contextual_report(150, context=context)

    assert proposals
    assert proposals == report["generatedProbeProposals"]
    assert proposals[0]["connectorAction"] == "open-resource-action"
    assert proposals[0]["invariantId"] == "external.connector_owned_rule"
    assert proposals[0]["routePattern"] == "/resource/{resourceId}/action?targetId={targetId}"
    assert proposals[0]["expectedStatus"] == 418
    assert {proposal["sourceParam"] for proposal in proposals} == {"targetId"}
    assert {proposal["mutationId"] for proposal in proposals} == {"connector-rule-a", "connector-rule-b"}
    assert {proposal["mutatedParams"]["targetId"] for proposal in proposals} == {
        "connector-value-a",
        "connector-value-b",
    }


def test_connector_action_graph_generates_bounded_sequence_proposals(monkeypatch: Any) -> None:
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "0")
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_EMBEDDINGS", "0")
    from bayesilisk.probe_proposals import generate_probe_proposals, generate_sequence_proposals
    from bayesilisk import reporting

    context = calcom_typed_action_graph_context()

    sequence_proposals = generate_sequence_proposals(context)
    proposals = generate_probe_proposals(context)
    report = reporting.build_contextual_report(150, context=context)

    assert sequence_proposals == proposals
    assert proposals == report["generatedProbeProposals"]
    proposal = proposals[0]
    assert proposal["proposalKind"] == "workflow-sequence"
    assert proposal["expectedStatus"] == 409
    assert [step["connectorAction"] for step in proposal["sequenceSteps"]] == [
        "create-booking",
        "cancel-booking",
        "open-public-booking-route",
    ]
    assert proposal["sequenceSteps"][-1]["params"] == {"rescheduleUid": "booking.uid"}


def test_connector_action_graph_supports_abag_typed_tokens(monkeypatch: Any) -> None:
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "0")
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_EMBEDDINGS", "0")
    from bayesilisk.probe_proposals import generate_sequence_proposals

    context = calcom_typed_action_graph_context()

    registry = schema_registry()
    validate_schema(context, registry["playwright-context.schema.json"], registry=registry)

    proposals = generate_sequence_proposals(context)

    assert len(proposals) == 1
    proposal = proposals[0]
    assert [step["connectorAction"] for step in proposal["sequenceSteps"]] == [
        "create-booking",
        "cancel-booking",
        "open-public-booking-route",
    ]
    assert proposal["sequenceSteps"][0]["produces"] == ["booking.uid", "booking.id", "eventType.slug", "user.username"]
    assert proposal["sequenceSteps"][0]["producesTokens"][0] == {
        "token": "resource.public_id",
        "resourceType": "booking",
        "refines": "booking.uid",
    }
    assert proposal["sequenceSteps"][-1]["params"] == {"rescheduleUid": "booking.uid"}
    assert proposal["sequenceSteps"][-1]["paramBindingTokens"]["rescheduleUid"] == {
        "token": "resource.public_id",
        "resourceType": "booking",
        "refines": "booking.uid",
    }


def test_abag_typed_tokens_do_not_fall_back_to_app_specific_refines() -> None:
    from bayesilisk.probe_proposals import generate_sequence_proposals

    context = {
        "connectorActionGraph": {
            "actions": [
                {
                    "actionId": "create-booking",
                    "produces": ["booking.uid"],
                },
                {
                    "actionId": "open-public-booking-route",
                    "requires": [],
                },
            ],
            "sequenceRules": [
                {
                    "ruleId": "typed-replay-needs-typed-producer",
                    "expectedBehavior": {"status": 409},
                    "goal": {
                        "action": "open-public-booking-route",
                        "paramBindings": {
                            "rescheduleUid": {
                                "token": "resource.public_id",
                                "resourceType": "booking",
                                "refines": "booking.uid",
                            }
                        },
                    },
                    "invariantId": "external.typed_replay_requires_typed_producer",
                    "title": "Typed replay requires typed producer",
                }
            ],
        }
    }

    assert generate_sequence_proposals(context) == []


def test_connector_action_graph_rejects_unsupported_sequences() -> None:
    from bayesilisk.probe_proposals import generate_sequence_proposals

    context = {
        "connectorActionGraph": {
            "actions": [
                {"actionId": "open-public-booking-route", "requires": []},
            ],
            "sequenceRules": [
                {
                    "ruleId": "missing-producer",
                    "expectedBehavior": {"status": 409},
                    "goal": {
                        "action": "open-public-booking-route",
                        "paramBindings": {
                            "rescheduleUid": {
                                "token": "resource.public_id",
                                "resourceType": "booking",
                                "refines": "booking.uid",
                            }
                        },
                    },
                    "invariantId": "external.missing_producer",
                    "requiresState": [
                        {"token": "state.cancelled", "resourceType": "booking"},
                    ],
                    "title": "Cannot build without producer actions",
                }
            ],
        }
    }

    assert generate_sequence_proposals(context) == []


def test_context_level_proposal_gates_reduce_repeated_fact_rules(monkeypatch: Any) -> None:
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "0")
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_EMBEDDINGS", "0")
    from bayesilisk.probe_proposals import generate_probe_proposals

    context = {
        "source": "connector-source-context",
        "proposalGates": [
            {
                "gateId": "shared-connector-gate",
                "invariantIds": [
                    "external.first_context_rule",
                    "external.second_context_rule",
                ],
                "rules": [
                    {
                        "param": "contextHandle",
                        "mutations": [
                            {"id": "shared-rule-a", "value": "shared-value-a"},
                            {"id": "shared-rule-b", "value": "shared-value-b"},
                        ],
                    },
                ],
            }
        ],
        "repositoryFacts": [
            {
                "availableActions": ["execute-first-action"],
                "expectedBehavior": {"status": 404},
                "invariantId": "external.first_context_rule",
                "params": [
                    {"kind": "opaque", "location": "query", "name": "contextHandle", "required": False},
                    {"kind": "opaque", "location": "query", "name": "controlHandle", "required": False},
                ],
                "routePattern": "/first?contextHandle={contextHandle}",
                "source": "repository-scan",
                "title": "First connector rule context",
            },
            {
                "availableActions": ["execute-second-action"],
                "expectedBehavior": {"status": 404},
                "invariantId": "external.second_context_rule",
                "params": [{"kind": "opaque", "location": "query", "name": "contextHandle", "required": False}],
                "routePattern": "/second?contextHandle={contextHandle}",
                "source": "repository-scan",
                "title": "Second connector rule context",
            },
        ],
    }

    proposals = generate_probe_proposals(context)

    assert len(proposals) == 4
    assert {proposal["proposalGate"] for proposal in proposals} == {"context-proposal-gate"}
    assert {proposal["sourceParam"] for proposal in proposals} == {"contextHandle"}
    assert {proposal["mutationId"] for proposal in proposals} == {"shared-rule-a", "shared-rule-b"}


def test_source_context_without_supplied_rules_emits_no_probe_proposals(monkeypatch: Any) -> None:
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "0")
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_EMBEDDINGS", "0")
    from bayesilisk.probe_proposals import generate_probe_proposals

    context = {
        "repositoryFacts": [
            {
                "availableActions": ["open-resource-action"],
                "expectedBehavior": {"status": 404},
                "invariantId": "external.no_rules_supplied",
                "params": [{"kind": "id", "location": "query", "name": "targetId", "required": True}],
                "routePattern": "/resource?targetId={targetId}",
                "source": "repository-scan",
                "title": "No supplied proposal rules",
            }
        ]
    }

    assert generate_probe_proposals(context) == []


def test_model_proposal_schema_covers_raw_proposal_payloads() -> None:
    registry = schema_registry()
    proposal_payload = {
        "scenarios": [
            {
                "title": "Weak model proposes support HR document probe",
                "targetPlane": "hr.documents_customer_role_boundary",
                "fragments": ["role.support_takeover_active", "hr.payroll_file_route"],
                "invariants": ["support.takeover_session_required", "hr.documents_customer_role_boundary"],
            }
        ]
    }
    invalid_payload = {
        "scenarios": [
            {
                "title": "Invents untrusted metadata",
                "targetPlane": "hr.documents_customer_role_boundary",
                "fragments": ["role.support_takeover_active", "hr.payroll_file_route"],
                "invariants": ["hr.documents_customer_role_boundary"],
                "productionObservation": "do not allow this field",
            }
        ]
    }

    validate_schema(proposal_payload, registry["model-proposals.schema.json"], registry=registry)
    try:
        validate_schema(invalid_payload, registry["model-proposals.schema.json"], registry=registry)
    except SchemaError:
        pass
    else:
        raise AssertionError("model proposal schema accepted an unexpected field")
