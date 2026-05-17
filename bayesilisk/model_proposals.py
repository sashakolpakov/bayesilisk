from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

from .catalog import FRAGMENTS
from .config import effective_runtime_config
from .invariants import INVARIANTS
from .types import Scenario
from .utils import (
    _extract_json_object,
    _dict_or_empty,
    _invariant_id_set,
    _redact_secrets,
    _safe_error,
    _safe_hash,
    _safe_hostname_class,
    _safe_url_class,
    _slug_id,
)

SCENARIO_PROPOSER_PROMPT_VERSION = "scenario-proposer.v1"

def _ollama_chat_json(
    messages: list[dict[str, str]],
    *,
    base_url: str,
    model: str,
    timeout: float,
) -> dict[str, Any]:
    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": float(os.environ.get("BAYESILISK_OLLAMA_SCENARIO_TEMPERATURE", "0.2")),
                "num_predict": int(os.environ.get("BAYESILISK_OLLAMA_SCENARIO_NUM_PREDICT", "1200")),
            },
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    content = data.get("message", {}).get("content", "")
    if not isinstance(content, str):
        return {}
    return _extract_json_object(content)


def _openai_compatible_chat_json(
    messages: list[dict[str, str]],
    *,
    api_key: str,
    base_url: str,
    model: str,
    timeout: float,
) -> dict[str, Any]:
    payload = json.dumps({"model": model, "messages": messages, "temperature": 0.2}).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not isinstance(content, str):
        return {}
    return _extract_json_object(content)


class ScenarioProposalProvider:
    name = "unknown"
    source = "unknown"
    requires_api_key = False

    def generate(self, prompt: list[dict[str, str]], config: dict[str, Any], api_key: str | None = None) -> dict[str, Any]:
        raise NotImplementedError


class OllamaScenarioProposalProvider(ScenarioProposalProvider):
    name = "ollama"
    source = "ollama-chat"

    def generate(self, prompt: list[dict[str, str]], config: dict[str, Any], api_key: str | None = None) -> dict[str, Any]:
        return _ollama_chat_json(
            prompt,
            base_url=config["ollamaBaseUrl"],
            model=config["scenarioModel"],
            timeout=config["scenarioTimeout"],
        )


class OpenAICompatibleScenarioProposalProvider(ScenarioProposalProvider):
    name = "openai-compatible"
    source = "openai-compatible-chat-completions"
    requires_api_key = True

    def generate(self, prompt: list[dict[str, str]], config: dict[str, Any], api_key: str | None = None) -> dict[str, Any]:
        return _openai_compatible_chat_json(
            prompt,
            api_key=api_key or "",
            base_url=config["scenarioBaseUrl"],
            model=config["scenarioModel"],
            timeout=config["scenarioTimeout"],
        )


SCENARIO_PROPOSAL_PROVIDERS: dict[str, ScenarioProposalProvider] = {
    "ollama": OllamaScenarioProposalProvider(),
    "openai": OpenAICompatibleScenarioProposalProvider(),
    "openai-compatible": OpenAICompatibleScenarioProposalProvider(),
}


def scenario_proposal_provider(name: str) -> ScenarioProposalProvider | None:
    return SCENARIO_PROPOSAL_PROVIDERS.get(name.strip().lower())


def _model_prompt(attention: dict[str, Any]) -> list[dict[str, str]]:
    top_planes = [
        {
            "attentionScore": plane.get("attentionScore"),
            "invariantId": plane.get("invariantId"),
            "reasons": plane.get("reasons", []),
        }
        for plane in attention.get("planes", [])[:6]
    ]
    catalog = {
        "allowedFragmentIds": [fragment.id for fragment in FRAGMENTS],
        "allowedInvariantIds": [invariant.id for invariant in INVARIANTS],
        "selectedPlaneIds": attention.get("selectedPlaneIds", []),
        "topPlanes": top_planes,
    }
    return [
        {
            "role": "system",
            "content": (
                "You propose Bayesilisk local verifier scenarios. Return JSON only. "
                "Use only allowedFragmentIds and allowedInvariantIds. Do not invent routes, facts, "
                "production observations, customer data, or new invariant names."
            ),
        },
        {
            "role": "user",
            "content": (
                "Create up to 3 scenario proposals near the selected high-attention planes. "
                "Shape: {\"scenarios\":[{\"title\":\"...\",\"targetPlane\":\"invariant.id\","
                "\"fragments\":[\"fragment.id\"],\"invariants\":[\"invariant.id\"]}]}\n\n"
                f"Catalog:\n{json.dumps(catalog, indent=2, sort_keys=True)}"
            ),
        },
    ]


def weak_model_raw_scenario_proposals(
    attention: dict[str, Any],
    runtime_config: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    config = effective_runtime_config(runtime_config)
    provider = {
        "enabled": config["enableScenarioProposer"],
        "source": "disabled",
    }
    if not provider["enabled"]:
        return [], provider
    provider_impl = scenario_proposal_provider(config["scenarioProvider"])
    prompt = _model_prompt(attention)
    provider.update(
        {
            "baseUrlClass": _safe_url_class(config["ollamaBaseUrl"]),
            "hostnameClass": _safe_hostname_class(config["scenarioBaseUrl"]),
            "model": config["scenarioModel"],
            "modelName": config["scenarioModel"],
            "promptHash": _safe_hash(prompt),
            "promptVersion": SCENARIO_PROPOSER_PROMPT_VERSION,
            "provider": config["scenarioProvider"],
            "source": "unknown",
            "sourceContext": attention.get("source", "none"),
        }
    )
    if provider_impl is None:
        provider["error"] = "unsupported-scenario-provider"
        return [], provider
    provider["provider"] = provider_impl.name
    provider["source"] = provider_impl.source
    api_key = config.get("scenarioApiKey") or ""
    provider["apiKeyConfigured"] = bool(api_key)
    if provider_impl.requires_api_key and not api_key:
        provider["error"] = "missing-api-key"
        return [], provider
    try:
        payload = provider_impl.generate(prompt, config, api_key=api_key)
    except Exception as exc:
        provider["error"] = _safe_error(exc)
        return [], provider
    scenarios = payload.get("scenarios", [])
    if not isinstance(scenarios, list):
        provider["error"] = "model response did not include a scenarios array"
        return [], provider
    provider["rawCount"] = len(scenarios)
    return [_redact_secrets(scenario) for scenario in scenarios if isinstance(scenario, dict)], provider


def validate_model_scenario_proposals(
    proposals: list[dict[str, Any]],
    attention: dict[str, Any],
    *,
    limit: int = 3,
    provider: dict[str, Any] | None = None,
) -> tuple[list[Scenario], list[dict[str, Any]]]:
    fragment_ids = {fragment.id for fragment in FRAGMENTS}
    invariant_ids = {invariant.id for invariant in INVARIANTS}
    attention = _dict_or_empty(attention)
    selected_planes = _invariant_id_set(attention, "selectedPlaneIds")
    scenarios: list[Scenario] = []
    rejected: list[dict[str, Any]] = []
    seen: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    provider = provider or {}
    for proposal in proposals:
        proposal_hash = _safe_hash(proposal)
        safe_proposal = _redact_secrets(proposal)
        if not isinstance(proposal, dict):
            rejected.append({"proposalHash": proposal_hash, "reason": "invalid-proposal-object", "proposal": safe_proposal})
            continue
        title = proposal.get("title")
        target_plane = proposal.get("targetPlane")
        fragments = proposal.get("fragments")
        invariants = proposal.get("invariants")
        if not isinstance(title, str) or not title.strip():
            rejected.append({"proposalHash": proposal_hash, "reason": "missing-title", "proposal": safe_proposal})
            continue
        if not isinstance(target_plane, str) or target_plane not in invariant_ids:
            rejected.append({"proposalHash": proposal_hash, "reason": "unknown-target-plane", "proposal": safe_proposal})
            continue
        if selected_planes and target_plane not in selected_planes:
            rejected.append({"proposalHash": proposal_hash, "reason": "target-plane-not-selected", "proposal": safe_proposal})
            continue
        if not isinstance(fragments, list) or not 2 <= len(fragments) <= 12:
            rejected.append({"proposalHash": proposal_hash, "reason": "invalid-fragment-count", "proposal": safe_proposal})
            continue
        if not isinstance(invariants, list) or not 1 <= len(invariants) <= 6:
            rejected.append({"proposalHash": proposal_hash, "reason": "invalid-invariant-count", "proposal": safe_proposal})
            continue
        fragment_tuple = tuple(item for item in fragments if isinstance(item, str))
        invariant_tuple = tuple(item for item in invariants if isinstance(item, str))
        if len(fragment_tuple) != len(fragments) or any(item not in fragment_ids for item in fragment_tuple):
            rejected.append({"proposalHash": proposal_hash, "reason": "unknown-fragment-id", "proposal": safe_proposal})
            continue
        if len(invariant_tuple) != len(invariants) or any(item not in invariant_ids for item in invariant_tuple):
            rejected.append({"proposalHash": proposal_hash, "reason": "unknown-invariant-id", "proposal": safe_proposal})
            continue
        if target_plane not in invariant_tuple:
            rejected.append({"proposalHash": proposal_hash, "reason": "target-plane-not-in-invariants", "proposal": safe_proposal})
            continue
        key = (fragment_tuple, invariant_tuple)
        if key in seen:
            rejected.append({"proposalHash": proposal_hash, "reason": "duplicate-proposal", "proposal": safe_proposal})
            continue
        seen.add(key)
        digest = proposal_hash[:8]
        provenance = {
            "accepted": True,
            "baseUrlClass": provider.get("baseUrlClass", "unknown"),
            "embeddingModel": attention.get("embeddingProvider", {}).get("model"),
            "modelName": provider.get("modelName", provider.get("model", "unknown")),
            "promptHash": provider.get("promptHash"),
            "promptVersion": provider.get("promptVersion", SCENARIO_PROPOSER_PROMPT_VERSION),
            "proposalHash": proposal_hash,
            "provider": provider.get("provider", "manual"),
            "source": provider.get("source", "validated-proposal"),
            "sourceContext": provider.get("sourceContext", attention.get("source", "none")),
            "targetPlane": target_plane,
        }
        scenarios.append(
            Scenario(
                f"generated.model.{len(scenarios) + 1:02d}.{_slug_id(target_plane)}.{digest}",
                "generated-weak-model-proposal",
                title.strip(),
                fragment_tuple,
                invariant_tuple,
                generated=True,
                generation_basis=f"weak-model-proposal:{target_plane}",
                provenance=provenance,
            )
        )
        if len(scenarios) >= limit:
            break
    return scenarios, rejected


def weak_model_scenarios(
    attention: dict[str, Any],
    runtime_config: dict[str, Any] | None = None,
) -> tuple[list[Scenario], dict[str, Any]]:
    config = effective_runtime_config(runtime_config)
    limit = config["scenarioProposalLimit"]
    raw, provider = weak_model_raw_scenario_proposals(attention, runtime_config=config)
    scenarios, rejected = validate_model_scenario_proposals(raw, attention, limit=limit, provider=provider)
    provider.update(
        {
            "acceptedCount": len(scenarios),
            "acceptedProposals": [scenario.provenance for scenario in scenarios],
            "rejected": rejected,
            "rejectedCount": len(rejected),
        }
    )
    return scenarios, provider
