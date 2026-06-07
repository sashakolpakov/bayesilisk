"""Offline entitlement gate for premium motif packs.

Premium packs are unlocked by an offline, signed license — no network calls, in
keeping with Bayesilisk's local-first ethos. The same mechanism serves a
commercial tier and an early-tester throttle: you issue signed tokens to whoever
you choose.

Trust model (Ed25519):
  - The vendor holds a private key and embeds the matching PUBLIC key here.
  - Each premium pack carries a `signature` over its canonical bytes (authenticity
    + integrity).
  - A license token is a signed `{licensee, packs, exp, iat}` payload; loading a
    premium pack requires a valid token covering that packId.

`cryptography` is imported lazily and only on the premium path, so the core /
free path stays zero-dependency. If it is absent, premium packs report as locked
with an install hint.
"""

from __future__ import annotations

import base64
import json
import os
import time
from typing import Any

# Replace with your real Ed25519 public key (base64url of the 32 raw bytes).
# `tools/bayesilisk_pack_sign.py keygen` prints the value to paste here.
# The BAYESILISK_VENDOR_PUBLIC_KEY env var overrides this (useful for testing).
VENDOR_PUBLIC_KEY_B64 = ""

INSTALL_HINT = "install signing support with: pip install 'bayesilisk[premium]'"


def _vendor_public_key_b64() -> str:
    return os.environ.get("BAYESILISK_VENDOR_PUBLIC_KEY", VENDOR_PUBLIC_KEY_B64).strip()


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _ed25519_public_key(public_key_b64: str):
    """Return a cryptography Ed25519PublicKey, or None if unavailable/invalid."""
    if not public_key_b64:
        return None
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except Exception:
        return None
    try:
        return Ed25519PublicKey.from_public_bytes(_b64url_decode(public_key_b64))
    except Exception:
        return None


def cryptography_available() -> bool:
    try:
        import cryptography  # noqa: F401
    except Exception:
        return False
    return True


def canonical_pack_bytes(pack: dict[str, Any]) -> bytes:
    """Canonical byte form a pack signature is computed over (signature removed)."""
    unsigned = {key: value for key, value in pack.items() if key != "signature"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _verify(public_key, signature: bytes, message: bytes) -> bool:
    try:
        public_key.verify(signature, message)
        return True
    except Exception:
        return False


def verify_pack_signature(pack: dict[str, Any], public_key_b64: str | None = None) -> bool:
    key = _ed25519_public_key(public_key_b64 if public_key_b64 is not None else _vendor_public_key_b64())
    signature = pack.get("signature")
    if key is None or not isinstance(signature, str) or not signature:
        return False
    return _verify(key, _b64url_decode(signature), canonical_pack_bytes(pack))


def verify_license(token: str, public_key_b64: str | None = None) -> dict[str, Any] | None:
    """Verify a license token and return its payload, or None if invalid/expired."""
    key = _ed25519_public_key(public_key_b64 if public_key_b64 is not None else _vendor_public_key_b64())
    if key is None or not isinstance(token, str) or token.count(".") != 1:
        return None
    payload_b64, signature_b64 = token.split(".", 1)
    if not _verify(key, _b64url_decode(signature_b64), payload_b64.encode("utf-8")):
        return None
    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    exp = payload.get("exp")
    if isinstance(exp, (int, float)) and not isinstance(exp, bool) and time.time() > exp:
        return None
    return payload


def _license_covers(payload: dict[str, Any], pack_id: str) -> bool:
    packs = payload.get("packs")
    if packs in ("*", ["*"]):
        return True
    return isinstance(packs, list) and pack_id in packs


def resolve_license(license_arg: str | None = None) -> str | None:
    """Resolve a license token from an explicit value/path or BAYESILISK_LICENSE."""
    source = license_arg or os.environ.get("BAYESILISK_LICENSE")
    if not source:
        return None
    source = source.strip()
    if "." in source and os.path.sep not in source and len(source) < 4096 and not os.path.exists(source):
        return source  # looks like an inline token
    try:
        if os.path.exists(source):
            return open(source, encoding="utf-8").read().strip()
    except OSError:
        return None
    return source


def pack_status(pack: dict[str, Any], license_token: str | None) -> dict[str, Any]:
    """Decide whether a pack is unlocked. Returns {unlocked, reason}."""
    tier = pack.get("tier")
    pack_id = pack.get("packId", "")
    if tier == "core":
        return {"unlocked": True, "reason": "core pack"}
    if not cryptography_available():
        return {"unlocked": False, "reason": f"premium pack requires signature verification; {INSTALL_HINT}"}
    if not _vendor_public_key_b64():
        return {"unlocked": False, "reason": "no vendor public key is configured for premium verification"}
    if not verify_pack_signature(pack):
        return {"unlocked": False, "reason": "premium pack signature is missing or invalid"}
    if not license_token:
        return {"unlocked": False, "reason": "no license token (set BAYESILISK_LICENSE or pass --license)"}
    payload = verify_license(license_token)
    if payload is None:
        return {"unlocked": False, "reason": "license token is invalid or expired"}
    if not _license_covers(payload, pack_id):
        return {"unlocked": False, "reason": f"license does not cover pack `{pack_id}`"}
    return {"unlocked": True, "reason": f"licensed to {payload.get('licensee', 'unknown')}"}
