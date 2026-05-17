from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass(frozen=True)
class Fragment:
    id: str
    domain: str
    kind: str
    facts: dict[str, Any]
    summary: str
    complete_alone: bool = False


@dataclass(frozen=True)
class Invariant:
    id: str
    layer: str
    expected: str
    prior: float
    fail_likelihood: float
    pass_likelihood: float
    difficulty: str
    evaluator: Callable[[dict[str, Any]], tuple[bool, str]]


@dataclass(frozen=True)
class Scenario:
    id: str
    tone: str
    title: str
    fragment_ids: tuple[str, ...]
    invariant_ids: tuple[str, ...]
    generated: bool = False
    generation_basis: str = "catalog"
    provenance: dict[str, Any] = field(default_factory=dict)
