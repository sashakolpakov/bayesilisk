#!/usr/bin/env python3
"""Vendor-side signing tool for Bayesilisk premium motif packs.

This is a maintainer utility, not part of the runtime. It needs `cryptography`
(`pip install 'bayesilisk[premium]'`). It produces artifacts that
`bayesilisk.motifs.entitlement` verifies offline:

  keygen          generate an Ed25519 keypair; prints the public key to embed
  sign-pack       sign a pack file in place / to --out (adds a `signature`)
  issue-license   mint a signed license token for a licensee

The canonical signing bytes and token format MUST stay in lock-step with
bayesilisk/motifs/entitlement.py.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from pathlib import Path


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _load_private_key(path: Path):
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    return load_pem_private_key(path.read_bytes(), password=None)


def _canonical_pack_bytes(pack: dict) -> bytes:
    unsigned = {key: value for key, value in pack.items() if key != "signature"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")


def cmd_keygen(args: argparse.Namespace) -> int:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    private_key = Ed25519PrivateKey.generate()
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    out = Path(args.out)
    out.write_bytes(pem)
    public_b64 = _b64url(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )
    print(f"private key written to {out}")
    print(f"public key (paste into entitlement.VENDOR_PUBLIC_KEY_B64):\n{public_b64}")
    return 0


def cmd_sign_pack(args: argparse.Namespace) -> int:
    private_key = _load_private_key(Path(args.key))
    pack = json.loads(Path(args.pack).read_text(encoding="utf-8"))
    signature = private_key.sign(_canonical_pack_bytes(pack))
    pack["signature"] = _b64url(signature)
    out = Path(args.out) if args.out else Path(args.pack)
    out.write_text(json.dumps(pack, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"signed pack `{pack.get('packId')}` -> {out}")
    return 0


def cmd_issue_license(args: argparse.Namespace) -> int:
    private_key = _load_private_key(Path(args.key))
    packs = ["*"] if args.packs.strip() == "*" else [p.strip() for p in args.packs.split(",") if p.strip()]
    payload = {
        "licensee": args.licensee,
        "packs": packs,
        "iat": int(time.time()),
        "exp": int(time.time()) + args.days * 86400,
    }
    payload_b64 = _b64url(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    signature_b64 = _b64url(private_key.sign(payload_b64.encode("utf-8")))
    token = f"{payload_b64}.{signature_b64}"
    if args.out:
        Path(args.out).write_text(token + "\n", encoding="utf-8")
        print(f"license for {args.licensee} (packs={packs}, {args.days}d) -> {args.out}")
    else:
        print(token)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="bayesilisk_pack_sign", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    keygen = sub.add_parser("keygen", help="Generate an Ed25519 keypair.")
    keygen.add_argument("--out", default="bayesilisk-vendor-key.pem", help="Private key output path.")
    keygen.set_defaults(func=cmd_keygen)

    sign = sub.add_parser("sign-pack", help="Sign a motif pack.")
    sign.add_argument("--pack", required=True, help="Pack JSON path.")
    sign.add_argument("--key", required=True, help="Private key PEM path.")
    sign.add_argument("--out", default=None, help="Output path (defaults to in place).")
    sign.set_defaults(func=cmd_sign_pack)

    lic = sub.add_parser("issue-license", help="Mint a signed license token.")
    lic.add_argument("--key", required=True, help="Private key PEM path.")
    lic.add_argument("--licensee", required=True, help="Licensee name.")
    lic.add_argument("--packs", default="*", help="Comma-separated pack ids, or * for all.")
    lic.add_argument("--days", type=int, default=90, help="Validity window in days.")
    lic.add_argument("--out", default=None, help="Token output path (defaults to stdout).")
    lic.set_defaults(func=cmd_issue_license)

    args = parser.parse_args()
    try:
        return int(args.func(args))
    except ImportError:
        print("This tool requires cryptography: pip install 'bayesilisk[premium]'", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
