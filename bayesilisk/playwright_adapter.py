from __future__ import annotations

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
        "expectedStatus": expected_status,
        "invariantId": _string_value(result.get("invariantId")),
        "observedStatus": observed_status,
        "passed": passed,
        "route": _string_value(result.get("route")),
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
                "expectedStatus": result["expectedStatus"],
                "invariantId": result["invariantId"],
                "observedStatus": result["observedStatus"],
                "passed": result["passed"],
                "route": result["route"],
                "source": "microsoft-playwright",
                "title": result["title"],
            }
            for result in normalized
        ],
        "playwrightProbe": {
            "failedCount": len(failures),
            "passedCount": len(normalized) - len(failures),
            "resultCount": len(normalized),
            "target": target,
        },
    }
