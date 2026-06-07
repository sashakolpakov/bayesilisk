"""Discover, validate, and gate motif packs.

The built-in core pack ships inside the package (bayesilisk/motifs/core/*.json)
and loads unconditionally. External packs come from the BAYESILISK_MOTIF_PACKS
environment variable (os.pathsep-separated files or directories) and explicit
caller paths; premium-tier packs pass through the entitlement gate.
"""

from __future__ import annotations

import json
import os
from importlib.resources import files
from pathlib import Path
from typing import Any, Iterable

from .entitlement import pack_status, resolve_license
from .validate import validate_pack

MOTIF_PACKS_ENV = "BAYESILISK_MOTIF_PACKS"


def _load_core_packs() -> list[dict[str, Any]]:
    packs: list[dict[str, Any]] = []
    try:
        core_dir = files("bayesilisk.motifs") / "core"
        entries = sorted((entry for entry in core_dir.iterdir() if entry.name.endswith(".json")), key=lambda e: e.name)
    except (FileNotFoundError, ModuleNotFoundError):
        return packs
    for entry in entries:
        try:
            packs.append(json.loads(entry.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    return packs


def _expand_sources(sources: Iterable[str]) -> list[Path]:
    paths: list[Path] = []
    for source in sources:
        if not source:
            continue
        path = Path(source).expanduser()
        if path.is_dir():
            paths.extend(sorted(p for p in path.glob("*.json")))
        elif path.is_file():
            paths.append(path)
    return paths


def _load_external_packs(extra_packs: Iterable[str]) -> list[dict[str, Any]]:
    sources: list[str] = []
    env_value = os.environ.get(MOTIF_PACKS_ENV, "")
    if env_value:
        sources.extend(env_value.split(os.pathsep))
    sources.extend(extra_packs)
    packs: list[dict[str, Any]] = []
    for path in _expand_sources(sources):
        try:
            packs.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    return packs


def load_packs(
    *,
    license_token: str | None = None,
    extra_packs: Iterable[str] = (),
    resolve: bool = True,
) -> list[dict[str, Any]]:
    """Load every discoverable pack with its lock status.

    Each entry: {packId, version, tier, title, valid, unlocked, reason,
    motifCount, errors, warnings, motifs}. `motifs` is populated only for valid
    unlocked packs. Deterministic order (by packId).
    """
    token = resolve_license(license_token) if resolve else license_token
    raw_packs = [*_load_core_packs(), *_load_external_packs(extra_packs)]
    registry: list[dict[str, Any]] = []
    for pack in raw_packs:
        validation = validate_pack(pack)
        status = pack_status(pack, token) if validation["accepted"] else {"unlocked": False, "reason": "invalid pack"}
        unlocked = validation["accepted"] and status["unlocked"]
        registry.append(
            {
                "packId": pack.get("packId", ""),
                "version": pack.get("version", ""),
                "tier": pack.get("tier", ""),
                "title": pack.get("title", ""),
                "valid": validation["accepted"],
                "unlocked": unlocked,
                "reason": status["reason"],
                "errors": validation["errors"],
                "warnings": validation["warnings"],
                "motifCount": len(pack.get("motifs", []) if isinstance(pack.get("motifs"), list) else []),
                "motifs": pack.get("motifs", []) if unlocked else [],
            }
        )
    registry.sort(key=lambda entry: entry["packId"])
    return registry


def available_motifs(
    *,
    license_token: str | None = None,
    extra_packs: Iterable[str] = (),
) -> list[dict[str, Any]]:
    """Flat, deterministic list of motifs from all unlocked packs (annotated with packId)."""
    motifs: list[dict[str, Any]] = []
    for entry in load_packs(license_token=license_token, extra_packs=extra_packs):
        for motif in entry["motifs"]:
            motifs.append({**motif, "packId": entry["packId"]})
    motifs.sort(key=lambda motif: (motif.get("packId", ""), motif.get("motifId", "")))
    return motifs
