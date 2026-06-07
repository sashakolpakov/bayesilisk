from __future__ import annotations

import base64
import importlib
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bayesilisk import motifs  # noqa: E402
from bayesilisk.connector_scan import infer_param_kind, scan_openapi  # noqa: E402
from bayesilisk.motifs import entitlement  # noqa: E402
from bayesilisk.probe_proposals import generate_probe_proposals  # noqa: E402
from bayesilisk.motifs.validate import validate_pack  # noqa: E402


def _source_fact_context() -> dict:
    return {
        "source": "test",
        "repositoryFacts": [
            {
                "source": "repository-scan",
                "title": "resource route",
                "invariantId": "app.resource",
                "routePattern": "/resource/{resourceId}",
                "availableActions": ["open-resource"],
                "params": [{"name": "resourceId", "kind": "id", "location": "path", "tokens": ["resource.id"]}],
            }
        ],
    }


def test_core_pack_loads_and_validates() -> None:
    packs = motifs.load_packs()
    core = [p for p in packs if p["packId"] == "bayesilisk.core.access-control"]
    assert core and core[0]["unlocked"] and core[0]["valid"]
    assert core[0]["motifCount"] >= 8
    avail = motifs.available_motifs()
    assert {"param-mutation", "workflow-sequence"} <= {m["kind"] for m in avail}


def test_binder_generates_proposals_with_motif_statuses() -> None:
    avail = motifs.available_motifs()
    bound = motifs.bind_motifs(_source_fact_context(), avail)
    proposals = generate_probe_proposals(bound)
    assert proposals
    statuses = {p["expectedStatus"] for p in proposals}
    assert 404 in statuses and 403 in statuses  # unknown-id and foreign-owned-id


def test_binding_is_deterministic() -> None:
    avail = motifs.available_motifs()
    first = motifs.bind_motifs(_source_fact_context(), avail)
    second = motifs.bind_motifs(_source_fact_context(), avail)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_workflow_sequence_binds_to_declared_action_graph() -> None:
    context = {
        "source": "test",
        "repositoryFacts": [],
        "connectorActionGraph": {
            "actions": [
                {"actionId": "create-booking", "produces": [{"token": "resource.public_id"}]},
                {"actionId": "cancel-booking", "produces": [{"token": "state.cancelled"}]},
                {"actionId": "open-public-route", "requires": [{"token": "resource.public_id"}]},
            ]
        },
    }
    avail = motifs.available_motifs()
    bound = motifs.bind_motifs(context, avail)
    rule_ids = {r["ruleId"] for r in bound["connectorActionGraph"]["sequenceRules"]}
    assert "motif.lifecycle.cancelled-replay" in rule_ids


def test_validate_pack_rejects_bad_pack() -> None:
    bad = {"packId": "Bad Pack", "version": "", "tier": "gold", "motifs": []}
    result = validate_pack(bad)
    assert not result["accepted"]
    assert any("packId" in e for e in result["errors"])
    assert any("tier" in e for e in result["errors"])


def test_scanner_infers_param_kinds_and_emits_validatable_context() -> None:
    assert infer_param_kind("bookingId", {"type": "string"}) == ("id", ["resource.id"])
    assert infer_param_kind("tenantId", {"type": "string"})[0] == "tenant-id"
    assert infer_param_kind("resetToken", {"type": "string"})[0] == "token"

    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Demo"},
        "paths": {
            "/bookings/{bookingId}": {
                "get": {
                    "operationId": "getBooking",
                    "parameters": [{"name": "bookingId", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {"200": {}, "404": {}},
                }
            }
        },
    }
    context = scan_openapi(spec)
    assert context["repositoryFacts"][0]["routePattern"] == "/bookings/{bookingId}"
    bound = motifs.bind_motifs(context, motifs.available_motifs())
    assert generate_probe_proposals(bound)


# --- Entitlement gate (requires cryptography) ---

crypto = pytest.importorskip("cryptography")
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _public_b64(key: Ed25519PrivateKey) -> str:
    from cryptography.hazmat.primitives import serialization

    return _b64url(
        key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
        )
    )


def _sign_pack(pack: dict, key: Ed25519PrivateKey) -> dict:
    signed = dict(pack)
    signed["signature"] = _b64url(key.sign(entitlement.canonical_pack_bytes(pack)))
    return signed


def _license(key: Ed25519PrivateKey, packs, exp_offset: int = 3600) -> str:
    payload = {"licensee": "Tester", "packs": packs, "iat": int(time.time()), "exp": int(time.time()) + exp_offset}
    payload_b64 = _b64url(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    return f"{payload_b64}.{_b64url(key.sign(payload_b64.encode()))}"


@pytest.fixture
def premium_pack() -> dict:
    return {
        "packId": "bayesilisk.premium.test",
        "version": "0.1.0",
        "tier": "premium",
        "motifs": [
            {
                "motifId": "premium.test-motif",
                "kind": "param-mutation",
                "family": "tenant-isolation",
                "severity": "high",
                "confidence": "heuristic",
                "rationale": "test",
                "appliesTo": {"paramKind": "id"},
                "mutation": {"id": "foreign", "valueTemplate": "foreign-{param}"},
                "expectedBehavior": {"status": 403},
            }
        ],
    }


def test_premium_pack_unlocks_with_valid_license(monkeypatch, premium_pack) -> None:
    key = Ed25519PrivateKey.generate()
    monkeypatch.setenv("BAYESILISK_VENDOR_PUBLIC_KEY", _public_b64(key))
    signed = _sign_pack(premium_pack, key)
    assert entitlement.pack_status(signed, _license(key, "*"))["unlocked"]
    assert entitlement.pack_status(signed, _license(key, ["bayesilisk.premium.test"]))["unlocked"]


def test_premium_pack_locked_without_or_with_bad_license(monkeypatch, premium_pack) -> None:
    key = Ed25519PrivateKey.generate()
    monkeypatch.setenv("BAYESILISK_VENDOR_PUBLIC_KEY", _public_b64(key))
    signed = _sign_pack(premium_pack, key)
    assert not entitlement.pack_status(signed, None)["unlocked"]
    assert not entitlement.pack_status(signed, _license(key, ["other.pack"]))["unlocked"]
    assert not entitlement.pack_status(signed, _license(key, "*", exp_offset=-10))["unlocked"]  # expired


def test_premium_pack_locked_when_tampered(monkeypatch, premium_pack) -> None:
    key = Ed25519PrivateKey.generate()
    monkeypatch.setenv("BAYESILISK_VENDOR_PUBLIC_KEY", _public_b64(key))
    signed = _sign_pack(premium_pack, key)
    signed["motifs"][0]["severity"] = "low"  # tamper after signing
    assert not entitlement.pack_status(signed, _license(key, "*"))["unlocked"]


def test_premium_pack_locked_under_foreign_key(monkeypatch, premium_pack) -> None:
    vendor, attacker = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    monkeypatch.setenv("BAYESILISK_VENDOR_PUBLIC_KEY", _public_b64(vendor))
    signed = _sign_pack(premium_pack, attacker)  # signed by the wrong key
    assert not entitlement.pack_status(signed, _license(attacker, "*"))["unlocked"]


# --- CLI + MCP surfaces ---


def test_cli_motifs_and_scan(tmp_path: Path) -> None:
    listing = subprocess.run(
        [sys.executable, "-m", "bayesilisk", "connector", "motifs"],
        check=True, cwd=REPO_ROOT, text=True, capture_output=True,
    )
    assert "bayesilisk.core.access-control" in listing.stderr

    spec = tmp_path / "openapi.json"
    spec.write_text(
        json.dumps(
            {
                "openapi": "3.0.0",
                "paths": {
                    "/items/{itemId}": {
                        "get": {
                            "operationId": "getItem",
                            "parameters": [{"name": "itemId", "in": "path", "required": True, "schema": {"type": "string"}}],
                            "responses": {"404": {}},
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "ctx.json"
    subprocess.run(
        [sys.executable, "-m", "bayesilisk", "connector", "scan", str(spec), "--bind-motifs", "--output", str(out)],
        check=True, cwd=REPO_ROOT, text=True, capture_output=True,
    )
    propose = subprocess.run(
        [sys.executable, "-m", "bayesilisk", "connector", "propose", str(out)],
        check=True, cwd=REPO_ROOT, text=True, capture_output=True,
    )
    assert json.loads(propose.stdout)


def test_mcp_list_and_bind_motifs() -> None:
    server = importlib.import_module("bayesilisk.mcp_server")
    listing = json.loads(
        server.handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "list_motifs", "arguments": {}}}
        )["result"]["content"][0]["text"]
    )
    assert any(p["packId"] == "bayesilisk.core.access-control" for p in listing["packs"])
    assert listing["motifs"]

    bound = json.loads(
        server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "bind_motifs", "arguments": {"sourceContext": _source_fact_context()}},
            }
        )["result"]["content"][0]["text"]
    )
    assert bound["proposals"]
    assert bound["boundMotifCount"] >= 8
