# Motif Library

The motif library is Bayesilisk's reusable, app-agnostic encoding of *which*
authorization and data-boundary bugs to hunt and *what the correct behavior is*.
A scanner discovers an app's surface; the motif library decides what to probe. A
motif never decides a verdict — it expands into the same `proposalRules` /
`connectorActionGraph.sequenceRules` the deterministic verifier already checks.

These are **category-theory motifs**: the library is structured as an abstract
category over the universal ABAG vocabulary, and each motif is a typed
diagram obligation rather than an app-specific script (see the *Category-theory
framing* section below).

## Category-theory framing

Bayesilisk's typed ABAG layer is a small category `A`, and the motifs live in it:

- **Objects** — universal ABAG tokens: typed states of a principal, resource,
  identifier, or session (`resource.public_id`, `state.cancelled`,
  `session.impersonated`, …). App nouns never appear here.
- **Morphisms** — connector actions, typed by `requires` (domain) and `produces`
  (codomain): e.g. `cancel : {resource.id} → {state.cancelled}`. The
  `connectorActionGraph` is the generating graph of `A`.
- **Composition** — `workflow-sequence` motifs are composite morphisms: bounded
  paths through the action graph (`create ∘ cancel ∘ replay`). The loop's sequence
  builder is composition with a depth bound.
- **Motif = a diagram obligation** — a `param-mutation` motif is a morphism on a
  single object asserting the expected arrow to a status object
  (`unknown : resource.public_id(absent) → 404`); a `workflow-sequence` motif is a
  diagram that must resolve to a *rejection* (the adversarial path must not commute
  into success). Verification checks whether the app's observed arrows agree with
  the motif's expected arrows.
- **The connector is a functor** `F : A → App`. `token` + `resourceType` name
  objects in `A`; `refines` is the concrete app handle. Bayesilisk reasons only in
  `A` (matching dependencies by `token` + `resourceType`, never by `refines`),
  while `F` executes through the concrete refinement. The existing boundary rule
  "match by token, execute by refines" is exactly functoriality.

Because motifs are stated in `A`, one motif fires on any app via its own functor
`F` — that is what makes the library reusable rather than app-specific.

## Motifs and packs

A **motif** is a template of two kinds:

- `param-mutation` — for a parameter of a given kind / ABAG token, an adversarial
  mutation and the expected secure status (e.g. unknown id → 404, foreign-owned
  id → 403, expired token → 401).
- `workflow-sequence` — an ABAG-typed multi-step pattern (e.g. create → cancel →
  replay public id → 409) bound to a connector action graph.

Each motif carries a `family` (mapped to access-control failure classes),
`severity`, `confidence`, `expectedBehavior`, and `references`.

Several core motifs are distilled from the worked {doc}`examples` Cal.com
connector run and carry a `validatedBy` note pointing at the real finding (some
with upstream human-authored fixes) — for example unknown-identifier → 404,
identifier-from-wrong-parent → 409, superseded-reset-token → 410, and the
cancelled-resource replay sequence → 409.

Motifs ship in **packs** with a `tier`:

- **core** — the free, open `bayesilisk.core.access-control` pack, shipped in the
  package and loaded unconditionally.
- **premium** — gated packs unlocked by an offline signed license (below).

## Using motifs

List packs and motifs (premium shows as locked without a license):

```sh
bayesilisk connector motifs
bayesilisk connector motifs --show bola.foreign-owned-id
```

Scan an OpenAPI spec into a draft source context and bind motifs to it:

```sh
bayesilisk connector scan openapi.json --bind-motifs --output source-context.json
bayesilisk connector validate source-context.json
bayesilisk connector propose source-context.json
```

Or bind motifs to a context you already have:

```sh
bayesilisk connector propose source-context.json --bind-motifs
```

Coding agents use the `list_motifs` and `bind_motifs` MCP tools for the same loop.

## Authoring and extending packs

A pack is a JSON file validated against `schemas/motif-pack.schema.json`. Point
Bayesilisk at extra packs with `--pack PATH` (file or directory) or the
`BAYESILISK_MOTIF_PACKS` environment variable (os-path-separated). Keep app nouns
out of motifs — use the universal ABAG token vocabulary (see {doc}`connectors`)
so a motif stays reusable across apps.

## Premium packs and licensing

Premium packs are unlocked by an **offline, signed license** — no network calls.
The mechanism serves both a commercial tier and an early-tester throttle: you
issue signed tokens to whoever you choose.

The vendor tool `tools/bayesilisk_pack_sign.py` (needs `pip install
'bayesilisk[premium]'`) does three things:

```sh
# 1. Generate a keypair; paste the printed public key into
#    bayesilisk/motifs/entitlement.py (VENDOR_PUBLIC_KEY_B64).
python tools/bayesilisk_pack_sign.py keygen --out vendor-key.pem

# 2. Sign a premium pack (adds a `signature`).
python tools/bayesilisk_pack_sign.py sign-pack --pack my-premium-pack.json --key vendor-key.pem

# 3. Mint a license token for a licensee.
python tools/bayesilisk_pack_sign.py issue-license --key vendor-key.pem \
  --licensee "Acme QA" --packs "*" --days 90 --out acme.token
```

Users supply the token via `--license acme.token` or `BAYESILISK_LICENSE`. A
premium pack loads only when its signature verifies against the embedded public
key **and** a valid, unexpired license covers its `packId`. Without
`cryptography` installed, premium packs report as locked with an install hint;
the core pack is unaffected. See `examples/motifs/premium-pack.example.json` for a
template.
