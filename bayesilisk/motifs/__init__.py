"""Bayesilisk motif library: app-agnostic, reusable probe motifs.

A motif encodes *what* authorization / data-boundary bug to hunt and *what the
correct behavior is*. Motifs ship in versioned packs (a free `core` tier plus
optional gated `premium` tiers) and bind to a connector source context, emitting
the `proposalRules` / `sequenceRules` the existing verifier expands. Motifs never
decide a verdict.
"""

from __future__ import annotations

from .binder import bind_motifs
from .entitlement import pack_status, resolve_license
from .loader import available_motifs, load_packs
from .validate import validate_pack

__all__ = [
    "available_motifs",
    "bind_motifs",
    "load_packs",
    "pack_status",
    "resolve_license",
    "validate_pack",
]
