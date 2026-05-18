from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .context import load_context, load_observations
from .probe_proposals import generate_probe_proposals
from .reporting import (
    build_contextual_report,
    build_report,
    issue_payloads,
    markdown_report,
    write_output,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bayesilisk Bayesian permission and scenario verifier.")
    parser.add_argument("--seed", type=int, default=150, help="Deterministic scenario ordering seed.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Report format.")
    parser.add_argument("--output", type=Path, default=None, help="Optional output file.")
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of findings.")
    parser.add_argument("--generated-count", type=int, default=8, help="Number of seeded generated composite scenarios.")
    parser.add_argument("--observations", type=Path, default=None, help="Optional JSON observation history.")
    parser.add_argument("--context", type=Path, default=None, help="Optional JSON context from agents, trackers, or repo scans.")
    parser.add_argument(
        "--probe-proposals-output",
        type=Path,
        default=None,
        help="Write generic connector probe proposals from --context and exit.",
    )
    embedding_group = parser.add_mutually_exclusive_group()
    embedding_group.add_argument(
        "--enable-embeddings",
        dest="enable_embeddings",
        action="store_true",
        default=None,
        help="Enable Ollama embedding similarities for Grassmann attention.",
    )
    embedding_group.add_argument(
        "--disable-embeddings",
        dest="enable_embeddings",
        action="store_false",
        help="Disable Ollama embedding similarities even if enabled by environment.",
    )
    proposer_group = parser.add_mutually_exclusive_group()
    proposer_group.add_argument(
        "--enable-scenario-proposer",
        dest="enable_scenario_proposer",
        action="store_true",
        default=None,
        help="Enable local Ollama scenario proposer generation.",
    )
    proposer_group.add_argument(
        "--disable-scenario-proposer",
        dest="enable_scenario_proposer",
        action="store_false",
        help="Disable scenario proposer generation even if enabled by environment.",
    )
    parser.add_argument("--embedding-model", default=None, help="Ollama embedding model name.")
    parser.add_argument("--scenario-provider", default=None, help="Scenario proposer provider name, e.g. ollama or openai-compatible.")
    parser.add_argument("--scenario-model", default=None, help="Scenario proposer model name.")
    parser.add_argument("--scenario-base-url", default=None, help="Scenario proposer HTTP base URL for non-Ollama providers.")
    parser.add_argument("--scenario-api-key-env", default=None, help="Environment variable name containing the scenario proposer API key.")
    parser.add_argument("--ollama-base-url", default=None, help="Ollama base URL for embeddings and scenario proposals.")
    parser.add_argument("--attention-threshold", type=float, default=None, help="Minimum attention score for selected planes.")
    parser.add_argument("--attention-selection-limit", type=int, default=None, help="Maximum selected attention planes.")
    parser.add_argument("--scenario-proposal-limit", type=int, default=None, help="Maximum accepted model-proposed scenarios.")
    parser.add_argument(
        "--issue-payloads",
        action="store_true",
        help="Emit only deduped issue payloads for ready failed findings.",
    )
    return parser.parse_args()


def runtime_config_from_args(args: argparse.Namespace) -> dict[str, Any]:
    config: dict[str, Any] = {}
    cli_to_config = {
        "attention_selection_limit": "attentionSelectionLimit",
        "attention_threshold": "attentionThreshold",
        "embedding_model": "embeddingModel",
        "enable_embeddings": "enableEmbeddings",
        "enable_scenario_proposer": "enableScenarioProposer",
        "ollama_base_url": "ollamaBaseUrl",
        "scenario_api_key_env": "scenarioApiKeyEnv",
        "scenario_base_url": "scenarioBaseUrl",
        "scenario_model": "scenarioModel",
        "scenario_proposal_limit": "scenarioProposalLimit",
        "scenario_provider": "scenarioProvider",
    }
    for cli_name, config_name in cli_to_config.items():
        value = getattr(args, cli_name)
        if value is not None:
            config[config_name] = value
    return config


def main() -> int:
    args = parse_args()
    observations = load_observations(args.observations)
    context = load_context(args.context)
    runtime_config = runtime_config_from_args(args)
    if args.probe_proposals_output is not None:
        content = json.dumps(generate_probe_proposals(context), indent=2, sort_keys=True) + "\n"
        write_output(content, args.probe_proposals_output)
        return 0
    if context:
        report = build_contextual_report(
            args.seed,
            limit=args.limit,
            generated_count=args.generated_count,
            observations=observations,
            context=context,
            runtime_config=runtime_config,
        )
    else:
        report = build_report(
            args.seed,
            limit=args.limit,
            generated_count=args.generated_count,
            observations=observations,
            runtime_config=runtime_config,
        )
    if args.issue_payloads:
        content = json.dumps(issue_payloads(report, context=context, limit=args.limit), indent=2, sort_keys=True) + "\n"
        write_output(content, args.output)
        return 0
    if args.format == "json":
        content = json.dumps(report, indent=2, sort_keys=True) + "\n"
    else:
        content = markdown_report(report)
    write_output(content, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
