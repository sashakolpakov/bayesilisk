# Bayesilisk

Bayesilisk is a deterministic local verifier for permission, entitlement, route, and data-boundary scenarios. It combines explicit rule invariants with Bayesian-style prioritization so agent workflows can produce reproducible JSON or Markdown findings.

Bayesilisk uses only local static scenarios, caller-provided context, optional observation history, and the Python standard library. It does not connect to production systems or inspect live customer data.

## Usage

Run the CLI from the repository root:

```sh
python3 -m bayesilisk --seed 150 --format json
python3 -m bayesilisk --seed 150 --format markdown --output /tmp/bayesilisk.md
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json --issue-payloads
```

Run the stdio MCP tool server:

```sh
python3 -m bayesilisk.mcp_server
```

After installing the package, the same entry points are available as `bayesilisk` and `bayesilisk-mcp`.

## Development

```sh
python3 -m pytest
```

See [docs/bayesilisk.md](docs/bayesilisk.md) for the full report contract, context ingestion format, and hardening workflow.
