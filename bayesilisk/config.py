from __future__ import annotations

import os
from typing import Any

from .utils import _dict_or_empty, _safe_hostname_class, _safe_url_class

def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _config_bool(overrides: dict[str, Any], key: str, default: bool) -> bool:
    value = overrides.get(key)
    if value is None:
        return default
    return bool(value)


def _config_int(overrides: dict[str, Any], key: str, default: int) -> int:
    value = overrides.get(key)
    if value is None:
        return default
    return int(value)


def _config_float(overrides: dict[str, Any], key: str, default: float) -> float:
    value = overrides.get(key)
    if value is None:
        return default
    return float(value)


def _config_str(overrides: dict[str, Any], key: str, default: str) -> str:
    value = overrides.get(key)
    if value is None:
        return default
    return str(value)


def effective_runtime_config(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    overrides = _dict_or_empty(overrides)
    env_ollama_base_url = os.environ.get("BAYESILISK_OLLAMA_BASE_URL", os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"))
    scenario_provider = _config_str(overrides, "scenarioProvider", os.environ.get("BAYESILISK_SCENARIO_PROVIDER", "ollama")).strip().lower()
    default_scenario_base_url = "https://api.openai.com/v1" if scenario_provider in {"openai", "openai-compatible"} else env_ollama_base_url
    scenario_base_url = _config_str(
        overrides,
        "scenarioBaseUrl",
        os.environ.get("BAYESILISK_SCENARIO_BASE_URL", default_scenario_base_url),
    )
    scenario_api_key_env = _config_str(
        overrides,
        "scenarioApiKeyEnv",
        os.environ.get("BAYESILISK_SCENARIO_API_KEY_ENV", ""),
    )
    scenario_api_key = overrides.get("scenarioApiKey")
    if scenario_api_key is None and scenario_api_key_env:
        scenario_api_key = os.environ.get(scenario_api_key_env)
    if scenario_api_key is None:
        scenario_api_key = os.environ.get("BAYESILISK_SCENARIO_API_KEY")
    if scenario_api_key is None and scenario_provider in {"openai", "openai-compatible"}:
        scenario_api_key = os.environ.get("OPENAI_API_KEY")
    if scenario_api_key is None and scenario_provider == "anthropic":
        scenario_api_key = os.environ.get("ANTHROPIC_API_KEY")
    return {
        "attentionSelectionLimit": max(1, _config_int(overrides, "attentionSelectionLimit", 4)),
        "attentionThreshold": max(0.0, min(1.0, _config_float(overrides, "attentionThreshold", 0.35))),
        "enableEmbeddings": _config_bool(
            overrides,
            "enableEmbeddings",
            _env_bool("BAYESILISK_USE_OLLAMA_EMBEDDINGS"),
        ),
        "enableScenarioProposer": _config_bool(
            overrides,
            "enableScenarioProposer",
            _env_bool("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL"),
        ),
        "embeddingModel": _config_str(overrides, "embeddingModel", os.environ.get("BAYESILISK_OLLAMA_MODEL", "nomic-embed-text")),
        "embeddingTimeout": _config_float(overrides, "embeddingTimeout", float(os.environ.get("BAYESILISK_OLLAMA_TIMEOUT", "30"))),
        "ollamaBaseUrl": _config_str(overrides, "ollamaBaseUrl", env_ollama_base_url),
        "scenarioApiKey": "" if scenario_api_key is None else str(scenario_api_key),
        "scenarioApiKeyEnv": scenario_api_key_env,
        "scenarioBaseUrl": scenario_base_url,
        "scenarioModel": _config_str(
            overrides,
            "scenarioModel",
            os.environ.get("BAYESILISK_OLLAMA_SCENARIO_MODEL", os.environ.get("OLLAMA_MODEL", "gemma4:e2b")),
        ),
        "scenarioProposalLimit": max(0, _config_int(overrides, "scenarioProposalLimit", int(os.environ.get("BAYESILISK_MODEL_SCENARIO_LIMIT", "3")))),
        "scenarioProvider": scenario_provider,
        "scenarioTimeout": _config_float(
            overrides,
            "scenarioTimeout",
            float(os.environ.get("BAYESILISK_OLLAMA_SCENARIO_TIMEOUT", "45")),
        ),
    }


def report_runtime_config(config: dict[str, Any] | None = None) -> dict[str, Any]:
    effective = effective_runtime_config(config)
    return {
        "attentionSelectionLimit": effective["attentionSelectionLimit"],
        "attentionThreshold": effective["attentionThreshold"],
        "embeddingModel": effective["embeddingModel"],
        "embeddingsEnabled": effective["enableEmbeddings"],
        "ollamaBaseUrlClass": _safe_url_class(effective["ollamaBaseUrl"]),
        "scenarioApiKeyConfigured": bool(effective.get("scenarioApiKey")),
        "scenarioBaseUrlClass": _safe_hostname_class(effective["scenarioBaseUrl"]),
        "scenarioModel": effective["scenarioModel"],
        "scenarioProposalLimit": effective["scenarioProposalLimit"],
        "scenarioProposerEnabled": effective["enableScenarioProposer"],
        "scenarioProvider": effective["scenarioProvider"],
    }
