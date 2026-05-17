from __future__ import annotations

from pathlib import Path
from typing import Any

PLAYWRIGHT_PRIOR_STEP = 0.06
PLAYWRIGHT_PRIOR_MAX = 0.18


def _string_value(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _int_value(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def normalize_probe_result(result: dict[str, Any]) -> dict[str, Any]:
    expected_status = _int_value(result.get("expectedStatus"))
    observed_status = _int_value(result.get("observedStatus"))
    passed = expected_status is not None and observed_status is not None and expected_status == observed_status
    return {
        "actorRole": _string_value(result.get("actorRole")),
        "artifactPaths": [str(value) for value in result.get("artifactPaths", []) if value],
        "expectedStatus": expected_status,
        "failureDetail": _string_value(result.get("failureDetail"), ""),
        "invariantId": _string_value(result.get("invariantId")),
        "networkResponses": result.get("networkResponses", []) if isinstance(result.get("networkResponses"), list) else [],
        "observedStatus": observed_status,
        "passed": passed,
        "route": _string_value(result.get("route")),
        "selector": _string_value(result.get("selector"), "[data-bayesilisk-probe]"),
        "targetUrl": _string_value(result.get("targetUrl"), ""),
        "timestamp": _string_value(result.get("timestamp"), ""),
        "title": _string_value(result.get("title"), "Playwright probe"),
    }


def build_context_from_probe_results(
    results: list[dict[str, Any]],
    *,
    source: str = "playwright-probe",
    target: str | None = None,
) -> dict[str, Any]:
    normalized = [normalize_probe_result(result) for result in results]
    failures = [result for result in normalized if not result["passed"]]
    prior_adjustments: dict[str, float] = {}
    for failure in failures:
        invariant_id = failure["invariantId"]
        if invariant_id == "unknown":
            continue
        prior_adjustments[invariant_id] = round(
            min(PLAYWRIGHT_PRIOR_MAX, prior_adjustments.get(invariant_id, 0.0) + PLAYWRIGHT_PRIOR_STEP),
            6,
        )

    agent_notes = [
        (
            "Microsoft Playwright observed route permission behavior for "
            f"`{result['route']}` as `{result['actorRole']}`: expected HTTP "
            f"{result['expectedStatus']}, observed HTTP {result['observedStatus']}; "
            f"invariant `{result['invariantId']}`; probe `{result['title']}`."
        )
        for result in failures
    ]
    if not agent_notes:
        agent_notes.append("Microsoft Playwright probe found no route permission mismatches.")

    return {
        "source": source,
        "agentNotes": agent_notes,
        "priorAdjustments": prior_adjustments,
        "repositoryFacts": [
            {
                "actorRole": result["actorRole"],
                "artifactPaths": result["artifactPaths"],
                "expectedStatus": result["expectedStatus"],
                "failureDetail": result["failureDetail"],
                "invariantId": result["invariantId"],
                "networkResponses": result["networkResponses"],
                "observedStatus": result["observedStatus"],
                "passed": result["passed"],
                "route": result["route"],
                "selector": result["selector"],
                "source": "microsoft-playwright",
                "targetUrl": result["targetUrl"] or target,
                "timestamp": result["timestamp"],
                "title": result["title"],
            }
            for result in normalized
        ],
        "playwrightProbe": {
            "artifactCount": sum(len(result["artifactPaths"]) for result in normalized),
            "failedCount": len(failures),
            "passedCount": len(normalized) - len(failures),
            "resultCount": len(normalized),
            "target": target,
        },
    }


def artifact_path(base_dir: Path, probe_index: int, name: str) -> str:
    safe_name = "".join(character if character.isalnum() or character in {"-", "_", "."} else "-" for character in name)
    return str(base_dir / f"probe-{probe_index + 1:02d}-{safe_name}")
