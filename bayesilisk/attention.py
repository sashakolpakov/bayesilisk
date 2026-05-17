from __future__ import annotations

import json
import urllib.request
from typing import Any

from .config import effective_runtime_config
from .constants import CONTEXT_INVARIANT_KEYWORDS, GRASSMANN_ATTENTION_WEIGHTS, INVARIANT_SENSITIVITY
from .context import _context_plane_facts, _context_strings, context_observations, context_summary, merge_observations
from .invariants import INVARIANTS
from .types import Invariant
from .utils import _invariant_id_set

def _normalize_vector(vector: list[float]) -> list[float]:
    norm = sum(value * value for value in vector) ** 0.5
    if norm <= 1e-10:
        return [0.0 for _ in vector]
    return [float(value) / norm for value in vector]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    limit = min(len(left), len(right))
    return sum(left[index] * right[index] for index in range(limit))


def _ollama_embed_texts(
    texts: list[str],
    *,
    base_url: str,
    model: str,
    timeout: float,
) -> list[list[float]]:
    if not texts:
        return []
    payload = json.dumps({"model": model, "input": texts}).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    embeddings = data.get("embeddings")
    if not isinstance(embeddings, list):
        raise ValueError("Ollama /api/embed response did not include embeddings")
    return [_normalize_vector([float(value) for value in embedding]) for embedding in embeddings]


def _plane_anchor_text(invariant: Invariant) -> str:
    keywords = " ".join(CONTEXT_INVARIANT_KEYWORDS.get(invariant.id, ()))
    return f"{invariant.id} {invariant.layer} {invariant.expected} {keywords}".strip()


def _context_attention_texts(context: dict[str, Any] | None) -> list[str]:
    if not context:
        return []
    texts: list[str] = []
    for fact in _context_plane_facts(context):
        texts.append(
            " ".join(
                str(value)
                for value in (
                    fact.get("source"),
                    fact.get("actorRole"),
                    fact.get("route"),
                    fact.get("invariantId"),
                    "passed" if fact.get("passed") else "failed",
                )
                if value
            )
        )
    for value in _context_strings(context):
        if value.strip():
            texts.append(value.strip())
    return texts[:24]


def embedding_plane_similarities(
    context: dict[str, Any] | None,
    runtime_config: dict[str, Any] | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    config = effective_runtime_config(runtime_config)
    if not config["enableEmbeddings"]:
        return {}, {"enabled": False}
    model = config["embeddingModel"]
    base_url = config["ollamaBaseUrl"]
    timeout = config["embeddingTimeout"]
    context_texts = _context_attention_texts(context)
    if not context_texts:
        return {}, {"enabled": True, "model": model, "baseUrl": base_url, "textCount": 0}
    plane_texts = [_plane_anchor_text(invariant) for invariant in INVARIANTS]
    try:
        embeddings = _ollama_embed_texts(
            [*plane_texts, *context_texts],
            base_url=base_url,
            model=model,
            timeout=timeout,
        )
    except Exception as exc:
        return {}, {
            "baseUrl": base_url,
            "enabled": True,
            "error": str(exc),
            "model": model,
            "textCount": len(context_texts),
        }
    plane_embeddings = embeddings[: len(plane_texts)]
    context_embeddings = embeddings[len(plane_texts) :]
    similarities = {}
    for invariant, plane_embedding in zip(INVARIANTS, plane_embeddings):
        best = max(
            (_cosine_similarity(plane_embedding, context_embedding) for context_embedding in context_embeddings),
            default=0.0,
        )
        similarities[invariant.id] = round(max(0.0, min(1.0, best)), 6)
    return similarities, {
        "baseUrl": base_url,
        "enabled": True,
        "model": model,
        "textCount": len(context_texts),
    }


def _attention_reason_list(
    failure_count: int,
    tested_count: int,
    playwright_count: int,
    sensitivity: float,
    keyword_hits: int,
    prior_adjustment: float,
    embedding_similarity: float,
    decay: float,
) -> list[str]:
    reasons: list[str] = []
    if failure_count:
        reasons.append("observed-failure-density")
    if tested_count == 0:
        reasons.append("untested-plane")
    if sensitivity >= 0.85:
        reasons.append("sensitive-invariant-plane")
    if playwright_count:
        reasons.append("playwright-evidence")
    if keyword_hits:
        reasons.append("context-keyword-near-plane")
    if embedding_similarity >= 0.55:
        reasons.append("ollama-embedding-near-plane")
    if prior_adjustment:
        reasons.append("context-prior-adjustment")
    if decay:
        reasons.append("fixed-or-muted-attention-decay")
    return reasons or ["baseline-plane"]


def _invariant_id_set(payload: dict[str, Any] | None, *keys: str) -> set[str]:
    if not isinstance(payload, dict):
        return set()
    invariant_ids = {invariant.id for invariant in INVARIANTS}
    found: set[str] = set()
    for key in keys:
        values = payload.get(key, [])
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, str) and value in invariant_ids:
                found.add(value)
    return found


def _attention_decay_by_invariant(
    context: dict[str, Any] | None,
    observations: dict[str, Any] | None,
) -> dict[str, float]:
    fixed = _invariant_id_set(context, "fixedInvariantIds", "regressionWatchInvariantIds") | _invariant_id_set(
        observations,
        "fixedInvariantIds",
        "regressionWatchInvariantIds",
    )
    muted = _invariant_id_set(context, "mutedInvariantIds") | _invariant_id_set(observations, "mutedInvariantIds")
    decay: dict[str, float] = {invariant_id: 0.12 for invariant_id in fixed}
    for invariant_id in muted:
        decay[invariant_id] = max(decay.get(invariant_id, 0.0), 0.2)
    return decay


def grassmann_attention(
    context: dict[str, Any] | None,
    observations: dict[str, Any] | None = None,
    runtime_config: dict[str, Any] | None = None,
    *,
    selection_limit: int = 4,
    selection_threshold: float = 0.35,
) -> dict[str, Any]:
    config = effective_runtime_config(runtime_config)
    selection_limit = config["attentionSelectionLimit"] if runtime_config is not None else selection_limit
    selection_threshold = config["attentionThreshold"] if runtime_config is not None else selection_threshold
    summary = context_summary(context)
    merged_observations = merge_observations(observations, context_observations(context))
    facts = _context_plane_facts(context)
    embedding_similarities, embedding_provider = embedding_plane_similarities(context, runtime_config=config)
    decay_by_invariant = _attention_decay_by_invariant(context, merged_observations)
    planes: list[dict[str, Any]] = []
    for invariant in INVARIANTS:
        plane_facts = [fact for fact in facts if fact["invariantId"] == invariant.id]
        tested_count = len(plane_facts)
        failure_count = len([fact for fact in plane_facts if not fact["passed"]])
        playwright_count = len([fact for fact in plane_facts if fact["source"] == "microsoft-playwright"])
        keyword_hits = int(summary["keywordHits"].get(invariant.id, 0))
        prior_adjustment = float(merged_observations.get("priorAdjustments", {}).get(invariant.id, 0.0))
        failure_density = failure_count / tested_count if tested_count else 0.0
        untestedness = 1.0 if tested_count == 0 else max(0.0, 1.0 - min(tested_count, 4) / 4.0)
        sensitivity = INVARIANT_SENSITIVITY.get(invariant.id, 0.5)
        playwright_evidence = min(1.0, playwright_count / 3.0)
        embedding_similarity = embedding_similarities.get(invariant.id, 0.0)
        novelty = max(min(1.0, keyword_hits / 6.0), embedding_similarity)
        decay = decay_by_invariant.get(invariant.id, 0.0)
        raw_score = (
            GRASSMANN_ATTENTION_WEIGHTS["failureDensity"] * failure_density
            + GRASSMANN_ATTENTION_WEIGHTS["untestedness"] * untestedness
            + GRASSMANN_ATTENTION_WEIGHTS["sensitivity"] * sensitivity
            + GRASSMANN_ATTENTION_WEIGHTS["playwrightEvidence"] * playwright_evidence
            + GRASSMANN_ATTENTION_WEIGHTS["novelty"] * novelty
            - decay
        )
        score = round(min(1.0, max(0.0, raw_score)), 6)
        planes.append(
            {
                "attentionScore": score,
                "failureCount": failure_count,
                "failureDensity": round(failure_density, 6),
                "embeddingSimilarity": round(embedding_similarity, 6),
                "decayForFixedOrMuted": round(decay, 6),
                "invariantId": invariant.id,
                "keywordHits": keyword_hits,
                "playwrightEvidence": round(playwright_evidence, 6),
                "priorAdjustment": round(prior_adjustment, 6),
                "reasons": _attention_reason_list(
                    failure_count,
                    tested_count,
                    playwright_count,
                    sensitivity,
                    keyword_hits,
                    prior_adjustment,
                    embedding_similarity,
                    decay,
                ),
                "sensitivity": sensitivity,
                "testedCount": tested_count,
                "untestedness": round(untestedness, 6),
            }
        )
    planes.sort(key=lambda item: (-item["attentionScore"], item["invariantId"]))
    selected = [
        plane["invariantId"]
        for plane in planes
        if plane["attentionScore"] >= selection_threshold
    ][:selection_limit]
    return {
        "boundedFeedback": True,
        "embeddingMode": (
            f"ollama:{embedding_provider.get('model')}"
            if embedding_provider.get("enabled") and not embedding_provider.get("error")
            else "grassmann-style-anchor-plane-proxy"
        ),
        "embeddingProvider": embedding_provider,
        "notes": (
            "Attention scores direct scenario exploration toward bad or under-tested planes. "
            "They do not decide invariant pass/fail."
        ),
        "planes": planes,
        "selectedPlaneIds": selected,
        "source": summary["source"],
        "weights": GRASSMANN_ATTENTION_WEIGHTS,
    }
