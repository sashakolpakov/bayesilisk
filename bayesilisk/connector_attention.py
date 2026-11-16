"""Attention over connector-defined goals, independent of the demo catalog.

Each goal spans a small subspace of text/token vectors. The geometric term is
the squared projection of the context vector onto an orthonormal basis (the
squared cosine of its angle to that subspace). It routes search, never verdicts.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Any

from .attention import _ollama_embed_texts
from .config import effective_runtime_config
from .utils import _safe_error


def _unit(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vector))
    return [x / norm for x in vector] if norm > 1e-10 else [0.0] * len(vector)


def subspace_projection(query: list[float], anchors: list[list[float]]) -> float:
    """Squared norm of projection; invariant to the choice of orthonormal basis."""
    if not query or any(len(anchor) != len(query) for anchor in anchors):
        return 0.0
    if not all(math.isfinite(x) for vector in [query, *anchors] for x in vector):
        return 0.0
    basis: list[list[float]] = []
    for anchor in anchors:
        residual = list(anchor)
        # Reorthogonalization avoids spurious dimensions for near-collinear anchors.
        for _ in range(2):
            for axis in basis:
                dot = sum(a * b for a, b in zip(residual, axis))
                residual = [a - dot * b for a, b in zip(residual, axis)]
        if sum(x * x for x in residual) > 1e-16:
            basis.append(_unit(residual))
    normalized = _unit(query)
    return min(1.0, max(0.0, sum(sum(a * b for a, b in zip(normalized, axis)) ** 2 for axis in basis)))


def _text_vector(text: str, dimensions: int = 256) -> list[float]:
    vector = [0.0] * dimensions
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        digest = hashlib.sha256(word.encode()).digest()
        vector[int.from_bytes(digest[:4], "big") % dimensions] += 1.0 if digest[4] & 1 else -1.0
    return _unit(vector)


def connector_attention(
    context: dict[str, Any],
    *,
    history: list[dict[str, Any]] | None = None,
    runtime_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = effective_runtime_config(runtime_config)
    graph = context.get("connectorActionGraph", {})
    graph = graph if isinstance(graph, dict) else {}
    rules = [rule for rule in graph.get("sequenceRules", []) if isinstance(rule, dict)] if isinstance(graph.get("sequenceRules", []), list) else []
    goals: dict[str, list[str]] = {}
    for rule in rules:
        invariant = rule.get("invariantId")
        if not isinstance(invariant, str) or not invariant:
            continue
        behavior = rule.get("expectedBehavior")
        behavior = behavior if isinstance(behavior, dict) else {}
        goals.setdefault(invariant, []).extend([
            str(rule.get("title", invariant)),
            str(behavior.get("description", invariant)),
            str(rule.get("requiresState", [])) + " " + str(rule.get("goal", {})),
        ])
    # Route-only connectors also get coverage telemetry, even without an ABAG.
    for fact in context.get("repositoryFacts", []):
        if isinstance(fact, dict) and isinstance(fact.get("invariantId"), str):
            goals.setdefault(fact["invariantId"], [str(fact.get("title", "")), str(fact.get("routePattern", ""))])
    observations = [fact for fact in [*(history or []), *context.get("repositoryFacts", [])]
                    if isinstance(fact, dict) and isinstance(fact.get("passed"), bool)]
    # Caller history and merged source context can contain the same execution.
    unique = {str(sorted(fact.items(), key=lambda item: item[0])): fact for fact in observations}
    observations = list(unique.values())
    query = " ".join(str(value) for value in [
        context.get("explorationFocus", ""), context.get("connectorInstructions", ""),
        *context.get("agentNotes", []),
        *[fact.get("failureDetail", "") for fact in observations if not fact["passed"]],
    ] if value)
    texts = [query, *[anchor for anchors in goals.values() for anchor in anchors]]
    embeddings = [_text_vector(text) for text in texts]
    provider: dict[str, Any] = {"enabled": config["enableEmbeddings"], "source": "local-hashed-text"}
    if config["enableEmbeddings"] and goals:
        try:
            candidate = _ollama_embed_texts(texts, base_url=config["ollamaBaseUrl"],
                                            model=config["embeddingModel"], timeout=config["embeddingTimeout"])
            if len(candidate) != len(texts) or not candidate[0] or any(len(v) != len(candidate[0]) for v in candidate):
                raise ValueError("embedding provider returned incompatible vectors")
            if not all(math.isfinite(x) for vector in candidate for x in vector):
                raise ValueError("embedding provider returned non-finite vectors")
            embeddings = candidate
            provider.update(source="ollama-embeddings", model=config["embeddingModel"])
        except Exception as exc:
            provider["error"] = _safe_error(exc)
    planes: list[dict[str, Any]] = []
    offset = 1
    fixed = set(context.get("fixedInvariantIds", []))
    muted = set(context.get("mutedInvariantIds", []))
    for invariant, anchors in goals.items():
        affinity = subspace_projection(embeddings[0], embeddings[offset:offset + len(anchors)])
        offset += len(anchors)
        observed = [fact for fact in observations if fact.get("invariantId") == invariant]
        tested = len(observed)
        failures = sum(not fact["passed"] for fact in observed)
        untested = 1.0 / (1.0 + tested)
        density = failures / tested if tested else 0.0
        decay = 0.2 if invariant in muted else 0.12 if invariant in fixed else 0.0
        score = min(1.0, max(0.0, 0.45 * affinity + 0.35 * untested + 0.2 * density - decay))
        reasons = ["connector-subspace-projection", "unexplored-goal" if not tested else "execution-feedback"]
        planes.append({
            "invariantId": invariant, "attentionScore": round(score, 6),
            "embeddingSimilarity": round(affinity, 6), "testedCount": tested,
            "failureCount": failures, "failureDensity": round(density, 6),
            "untestedness": round(untested, 6), "decayForFixedOrMuted": decay,
            "keywordHits": 0, "playwrightEvidence": 0.0, "priorAdjustment": 0.0,
            "sensitivity": 0.5, "reasons": reasons,
        })
    planes.sort(key=lambda plane: (-plane["attentionScore"], plane["invariantId"]))
    selected = [plane["invariantId"] for plane in planes if plane["attentionScore"] >= config["attentionThreshold"]]
    if not selected and planes:
        selected = [planes[0]["invariantId"]]
    return {
        "boundedFeedback": True, "source": "connector-defined-invariants",
        "embeddingMode": "orthonormal-subspace-projection", "embeddingProvider": provider,
        "selectedPlaneIds": selected[:config["attentionSelectionLimit"]], "planes": planes,
        "weights": {"subspaceProjection": 0.45, "untestedness": 0.35, "failureDensity": 0.2},
    }
