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


def test_golden_baseline_report_matches_report_schema(monkeypatch: Any) -> None:
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "0")
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_EMBEDDINGS", "0")
    from bayesilisk import bayesilisk

    registry = schema_registry()
    golden = load_json(FIXTURE_DIR / "baseline_report.json")
    current = bayesilisk.build_report(150)

    validate_schema(golden, registry["report.schema.json"], registry=registry)
    validate_schema(current, registry["report.schema.json"], registry=registry)
    assert canonical_report(current) == golden


def test_golden_playwright_context_report_matches_schemas(monkeypatch: Any) -> None:
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "0")
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_EMBEDDINGS", "0")
    from bayesilisk import bayesilisk

    registry = schema_registry()
    context = load_json(FIXTURE_DIR / "playwright_context.json")
    golden = load_json(FIXTURE_DIR / "playwright_context_report.json")
    current = bayesilisk.build_contextual_report(150, context=context)

    validate_schema(context, registry["playwright-context.schema.json"], registry=registry)
    validate_schema(golden, registry["report.schema.json"], registry=registry)
    validate_schema(current, registry["report.schema.json"], registry=registry)
    assert canonical_report(current) == golden


def test_current_issue_payloads_match_schema() -> None:
    from bayesilisk import bayesilisk

    registry = schema_registry()
    report = bayesilisk.build_report(150)
    payloads = bayesilisk.issue_payloads(report)

    assert payloads
    for payload in payloads:
        validate_schema(payload, registry["issue-payload.schema.json"], registry=registry)


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
