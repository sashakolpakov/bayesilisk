from __future__ import annotations

import copy
import importlib
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bayesilisk import connector_exploration as exploration
from bayesilisk.connector_attention import connector_attention, subspace_projection
from bayesilisk.connector_loop import advance
from bayesilisk.connector_orchestration import verify_connector_outputs
from bayesilisk.probe_proposals import generate_probe_proposals

IDENTIFIER = {"token": "resource.public_id", "resourceType": "booking", "refines": "booking.uid"}
CANCELLED = {"token": "state.cancelled", "resourceType": "booking"}
EXPIRED = {"token": "state.expired", "resourceType": "booking"}


@pytest.fixture
def context() -> dict:
    result = {
        "source": "independent-booking-fixture",
        "connectorInstructions": "Create a local booking, change its state, and exercise the public read handler.",
        "explorationFocus": "cancelled booking identifier replay",
        "repositoryFacts": [],
        "connectorActionGraph": {
            "actions": [
                # The legacy first-producer planner gets stuck here. The model
                # must discover the other declared producer, not select its output.
                {"actionId": "create-authenticated", "requires": [{"token": "session.authenticated"}], "produces": [IDENTIFIER]},
                {"actionId": "create-fixture", "produces": [IDENTIFIER]},
                {"actionId": "cancel", "requires": [IDENTIFIER], "produces": [CANCELLED]},
                {"actionId": "expire", "requires": [CANCELLED], "produces": [EXPIRED]},
                {"actionId": "read", "requires": [IDENTIFIER], "paramBindings": {"uid": IDENTIFIER}},
            ],
            "sequenceRules": [
                {"ruleId": "cancelled-replay", "invariantId": "booking.cancelled_replay", "maxDepth": 6,
                 "title": "Cancelled booking identifier replay", "expectedBehavior": {"status": 409},
                 "requiresState": [CANCELLED], "goal": {"action": "read", "paramBindings": {"uid": IDENTIFIER}}},
                {"ruleId": "expired-replay", "invariantId": "booking.expired_replay", "maxDepth": 8,
                 "title": "Expired booking identifier replay", "expectedBehavior": {"status": 410},
                 "requiresState": [EXPIRED], "goal": {"action": "read", "paramBindings": {"uid": IDENTIFIER}}},
            ],
        },
    }
    return json.loads(json.dumps(result))


def candidate(actions: list[str] | None = None, rule: str = "cancelled-replay") -> dict:
    return {"title": "A model-proposed replay", "sequenceRuleId": rule,
            "sequenceSteps": [{"connectorAction": action} for action in (actions or ["create-fixture", "cancel", "read"])]}


def test_model_can_find_a_path_the_first_producer_planner_misses(context: dict) -> None:
    assert generate_probe_proposals(context) == []
    admitted, rejected = exploration.validate_connector_scenarios([candidate()], context)
    assert not rejected
    proposal = admitted[0]
    assert [step["connectorAction"] for step in proposal["sequenceSteps"]] == ["create-fixture", "cancel", "read"]
    assert proposal["expectedStatus"] == 409
    assert proposal["sequenceSteps"][-1]["paramBindingTokens"]["uid"] == IDENTIFIER
    assert proposal["sequenceSteps"][-1]["params"] == {"uid": "booking.uid"}


@pytest.mark.parametrize("mutate, reason", [
    (lambda raw: raw.update(expectedStatus=200), "oracle/observation"),
    (lambda raw: raw.update(passed=True), "oracle/observation"),
    (lambda raw: raw.update(sequenceRuleId="invented"), "unknown or ambiguous"),
    (lambda raw: raw.update(targetPlane="invented"), "targetPlane"),
    (lambda raw: raw["sequenceSteps"][0].update(connectorAction="undeclared"), "unknown connectorAction"),
    (lambda raw: raw.update(sequenceSteps=[{"connectorAction": "cancel"}, {"connectorAction": "create-fixture"}, {"connectorAction": "read"}]), "dependencies"),
    (lambda raw: raw.update(sequenceSteps=[{"connectorAction": "create-fixture"}, {"connectorAction": "read"}]), "goal state"),
    (lambda raw: raw.update(sequenceSteps=[{"connectorAction": "create-fixture"}] * 7), "over-depth"),
    (lambda raw: raw["sequenceSteps"][0].update(producesTokens=[EXPIRED]), "token signature"),
    (lambda raw: raw["sequenceSteps"][-1].update(paramBindingTokens={"evil": IDENTIFIER}), "undeclared parameter"),
    (lambda raw: raw["sequenceSteps"][-1].update(paramBindingTokens={"uid": {**IDENTIFIER, "resourceType": "invoice"}}), "token type"),
    (lambda raw: raw["sequenceSteps"][-1].update(paramBindingTokens={"uid": {**IDENTIFIER, "refines": "other.uid"}}), "refinement"),
    (lambda raw: raw.update(sequenceSteps=[{"reuseProposalId": "not-admitted"}]), "unknown retained"),
])
def test_invalid_model_sequences_never_reach_execution(context: dict, mutate, reason: str) -> None:
    raw = candidate()
    mutate(raw)
    admitted, rejected = exploration.validate_connector_scenarios([raw], context)
    assert admitted == []
    assert reason in rejected[0]["reason"]


def test_qualified_tokens_and_concrete_bindings_must_be_available(context: dict) -> None:
    changed = copy.deepcopy(context)
    changed["connectorActionGraph"]["actions"][1]["produces"][0]["resourceType"] = "invoice"
    assert "dependencies" in exploration.validate_connector_scenarios([candidate()], changed)[1][0]["reason"]
    changed = copy.deepcopy(context)
    changed["connectorActionGraph"]["actions"][1]["produces"][0]["refines"] = "invoice.uid"
    assert "concrete refinement" in exploration.validate_connector_scenarios([candidate()], changed)[1][0]["reason"]


def test_binding_type_and_refinement_need_the_same_produced_witness(context: dict) -> None:
    context["connectorActionGraph"]["actions"][1]["produces"] = [
        {**IDENTIFIER, "refines": "other.uid"},
        {**IDENTIFIER, "resourceType": "invoice"},
    ]
    admitted, rejected = exploration.validate_connector_scenarios([candidate()], context)
    assert not admitted and "concrete refinement" in rejected[0]["reason"]


def test_terminal_goals_preserve_action_arguments_and_type_constraints(context: dict) -> None:
    tenant = {"token": "scope.tenant", "resourceType": "booking", "refines": "booking.tenant"}
    context["connectorActionGraph"]["actions"][1]["produces"].append(tenant)
    context["connectorActionGraph"]["actions"][-1]["paramBindings"]["tenantId"] = tenant
    admitted, rejected = exploration.validate_connector_scenarios([candidate()], context)
    assert not rejected
    assert admitted[0]["sequenceSteps"][-1]["params"] == {"uid": "booking.uid", "tenantId": "booking.tenant"}
    context["connectorActionGraph"]["sequenceRules"][0]["goal"]["paramBindings"]["uid"] = {**IDENTIFIER, "resourceType": "invoice"}
    assert "conflicts" in exploration.validate_connector_scenarios([candidate()], context)[1][0]["reason"]


def test_duplicates_and_zero_admission_budget(context: dict) -> None:
    accepted, rejected = exploration.validate_connector_scenarios([candidate(), candidate()], context)
    assert len(accepted) == 1 and rejected[0]["reason"] == "duplicate sequence"
    assert exploration.validate_connector_scenarios([candidate()], context, limit=0)[0] == []


def test_real_subspace_projection_and_connector_coverage(context: dict) -> None:
    assert subspace_projection([1, 1, 0], [[1, 0, 0], [0, 1, 0]]) == pytest.approx(1)
    assert subspace_projection([1, 1, 0], [[1, 1, 0], [1, -1, 0]]) == pytest.approx(1)
    assert subspace_projection([0, 0, 1], [[1, 0, 0], [0, 1, 0]]) == 0
    assert subspace_projection([1, 0], [[float("nan"), 0]]) == 0
    attention = connector_attention(context)
    assert {plane["invariantId"] for plane in attention["planes"]} == {"booking.cancelled_replay", "booking.expired_replay"}
    history = [{"invariantId": "booking.cancelled_replay", "passed": True}]
    after = connector_attention(context, history=history)
    before_score = next(plane["attentionScore"] for plane in attention["planes"] if plane["invariantId"] == "booking.cancelled_replay")
    after_score = next(plane["attentionScore"] for plane in after["planes"] if plane["invariantId"] == "booking.cancelled_replay")
    assert after_score < before_score


def _execute(proposal: dict) -> dict:
    # Independent fixture execution, rather than copying expectedStatus into an
    # observation. The result comes from a stateful handler with its own rules.
    booking = None
    executed = []
    observed = None
    for step in proposal["sequenceSteps"]:
        action = step["connectorAction"]
        if action == "create-fixture":
            booking = {"uid": "fixture-1", "cancelled": False, "expired": False}
        elif action == "cancel":
            booking["cancelled"] = True
        elif action == "expire":
            booking["expired"] = True
        elif action == "read":
            observed = 410 if booking["expired"] else 409 if booking["cancelled"] else 200
        else:
            raise AssertionError(action)
        executed.append(action)
    return {"source": "local-fixture", "repositoryFacts": [{
        "proposalId": proposal["proposalId"], "executedActions": executed,
        "actorRole": "test", "artifactPaths": [], "failureDetail": "", "networkResponses": [],
        "expectedStatus": proposal["expectedStatus"], "observedStatus": observed,
        "passed": observed == proposal["expectedStatus"], "invariantId": proposal["invariantId"],
        "route": "/bookings/{uid}", "selector": "connector:read", "source": "local-fixture",
        "targetUrl": "http://localhost/bookings/fixture-1", "timestamp": "2026-11-16T12:00:00Z", "title": proposal["title"],
    }]}


def test_loop_retains_only_executed_paths_then_composes_them(context: dict, monkeypatch) -> None:
    requests = []

    class Provider:
        requires_api_key = False

        def generate(self, prompt, config, api_key=None):
            contract = json.loads(prompt[1]["content"])
            requests.append(contract)
            if not contract["retainedSequences"]:
                return {"scenarios": [candidate()]}
            previous = contract["retainedSequences"][0]["proposal"]["proposalId"]
            return {"scenarios": [{"title": "Extend the retained replay", "sequenceRuleId": "expired-replay",
                                   "sequenceSteps": [{"reuseProposalId": previous}, {"connectorAction": "expire"}, {"connectorAction": "read"}]}]}

    monkeypatch.setattr(exploration, "scenario_proposal_provider", lambda _: Provider())
    start = advance(None, source_context=context, runtime_config={"enableScenarioProposer": True, "scenarioApiKey": "keep-private"})
    assert start["phase"] == "await-connector"
    assert start["state"]["explorationMemory"]["retainedSequences"] == []
    assert "keep-private" not in json.dumps(start)
    proposal = start["proposals"][0]
    next_round = advance(start["state"], observed_context=_execute(proposal))
    assert len(requests) == 2  # enable flag persisted; no catalog-only fallback
    assert next_round["retainedSequenceCount"] == 1
    grown = next_round["proposals"][0]
    assert grown["reusedProposalIds"] == [proposal["proposalId"]]
    assert [step["connectorAction"] for step in grown["sequenceSteps"]] == ["create-fixture", "cancel", "read", "expire", "read"]
    assert grown["expectedStatus"] == 410
    assert next_round["report"]["grassmannAttention"]["embeddingMode"] == "orthonormal-subspace-projection"
    assert next_round["report"]["proposedByModel"]["acceptedCount"] == 1
    verified = verify_connector_outputs({"sourceContext": next_round["state"]["sourceContext"], "scenarioPlan": next_round["scenarioPlan"],
                                          "provenance": {"provenanceId": "local"}, "observedContext": _execute(grown)})
    assert verified["observationValidation"]["accepted"]
    assert len(requests) == 2  # verification replays the saved plan, not the LLM
    assert verified["report"]["generatedProbeProposals"][0]["proposalId"] == grown["proposalId"]
    contracts = importlib.import_module("test_report_contracts")
    contracts.validate_schema(verified["report"], contracts.schema_registry()["report.schema.json"],
                              registry=contracts.schema_registry())
    changed = copy.deepcopy(context)
    changed["connectorVersion"] = "changed-implementation"
    blocked = advance(next_round["state"], source_context=changed)
    assert blocked["phase"] == "blocked" and "Source contract changed" in blocked["nextAction"]


def test_saved_plan_and_receipts_are_rechecked(context: dict) -> None:
    proposal = exploration.validate_connector_scenarios([candidate()], context)[0][0]
    plan = {"acceptedScenarios": [proposal]}
    observed = _execute(proposal)
    base = {"sourceContext": context, "scenarioPlan": plan, "observedContext": observed,
            "provenance": {"provenanceId": "local"}}
    assert verify_connector_outputs(base)["observationValidation"]["accepted"]
    forged = copy.deepcopy(base)
    forged["observedContext"]["repositoryFacts"][0].update(expectedStatus=200, passed=False)
    assert not verify_connector_outputs(forged)["observationValidation"]["accepted"]
    incomplete = copy.deepcopy(base)
    incomplete["observedContext"]["repositoryFacts"][0]["executedActions"] = ["read"]
    assert not verify_connector_outputs(incomplete)["observationValidation"]["accepted"]
    stale = copy.deepcopy(base)
    stale["sourceContext"]["connectorActionGraph"]["sequenceRules"][0]["expectedBehavior"]["status"] = 403
    assert not verify_connector_outputs(stale)["observationValidation"]["accepted"]
    memory = exploration.remember_executions({}, plan, observed)
    assert exploration.remember_executions(memory, plan, observed)["retainedSequences"][0]["executionCount"] == 1
    reuse = {"title": "reuse", "sequenceRuleId": "cancelled-replay",
             "sequenceSteps": [{"reuseProposalId": proposal["proposalId"]}]}
    assert exploration.validate_connector_scenarios([reuse], context, retained=memory["retainedSequences"])[0]
    assert not exploration.validate_connector_scenarios([reuse], stale["sourceContext"], retained=memory["retainedSequences"])[0]
    assert not verify_connector_outputs({**base, "scenarioPlan": {}})["observationValidation"]["accepted"]


@pytest.mark.parametrize("identity", ["original", "renamed", "missing"])
def test_plan_origin_labels_cannot_bypass_source_oracles(context: dict, identity: str) -> None:
    proposal = exploration.validate_connector_scenarios([candidate()], context)[0][0]
    observed = _execute(proposal)
    proposal.pop("proposalGate")
    if identity == "renamed":
        proposal["proposalId"] = "untrusted-renamed-id"
    elif identity == "missing":
        proposal.pop("proposalId")
    proposal["expectedStatus"] = 200
    fact = observed["repositoryFacts"][0]
    fact.update(proposalId=proposal.get("proposalId"), expectedStatus=200, observedStatus=200, passed=True)
    verified = verify_connector_outputs({"sourceContext": context, "scenarioPlan": {"acceptedScenarios": [proposal]},
                                          "observedContext": observed, "provenance": {"provenanceId": "local"}})
    assert not verified["observationValidation"]["accepted"]


def test_saved_parameter_probe_oracle_is_grounded_in_source(context: dict) -> None:
    source = {"source": "source", "repositoryFacts": [{
        "source": "repository-scan", "title": "Unknown uid", "invariantId": "booking.unknown_uid",
        "routePattern": "/bookings/{uid}", "params": [{"name": "uid", "kind": "id"}],
        "availableActions": ["read"], "expectedBehavior": {"status": 404},
        "proposalRules": {"uid": [{"id": "unknown-id", "value": "missing"}]},
    }]}
    proposal = generate_probe_proposals(source)[0]
    observed = _execute(exploration.validate_connector_scenarios([candidate()], context)[0][0])
    fact = observed["repositoryFacts"][0]
    fact.pop("executedActions")
    fact.update(proposalId=proposal["proposalId"], invariantId=proposal["invariantId"],
                expectedStatus=404, observedStatus=200, passed=False)
    base = {"sourceContext": source, "scenarioPlan": {"acceptedScenarios": [proposal]},
            "observedContext": observed, "provenance": {"provenanceId": "local"}}
    assert verify_connector_outputs(base)["observationValidation"]["accepted"]
    proposal["expectedStatus"] = 200
    fact.update(expectedStatus=200, passed=True)
    assert not verify_connector_outputs(base)["observationValidation"]["accepted"]


def test_mcp_accepts_external_model_drafts(context: dict) -> None:
    server = importlib.import_module("bayesilisk.mcp_server")
    response = server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "scenario_plan", "arguments": {"sourceContext": context, "provenance": {"provenanceId": "local"},
                                                    "draftPlan": {"scenarios": [candidate()]}}}})
    result = json.loads(response["result"]["content"][0]["text"])
    assert result["validation"]["accepted"]
    assert result["scenarioPlan"]["acceptedScenarios"][0]["proposalGate"] == "validated-model-abag-sequence"


def test_mcp_respects_zero_limit_and_rejects_malformed_drafts(context: dict, monkeypatch) -> None:
    server = importlib.import_module("bayesilisk.mcp_server")
    monkeypatch.setattr(exploration, "scenario_proposal_provider", lambda _: pytest.fail("zero budget must not call a model"))

    def call(arguments):
        return server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "propose_probes", "arguments": {"context": context, **arguments}}})

    response = call({"limit": 0, "enableScenarioProposer": True})
    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["proposalCount"] == 0
    assert "error" in call({"draftPlan": {}})


def test_cli_provider_transport_and_private_credentials(context: dict, tmp_path: Path) -> None:
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            requests.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            assert self.headers["Authorization"] == "Bearer test-credential"
            body = json.dumps({"choices": [{"message": {"content": json.dumps({"scenarios": [candidate()]})}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    source = tmp_path / "source.json"
    plan = tmp_path / "plan.json"
    source.write_text(json.dumps(context))
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        result = subprocess.run([sys.executable, "-m", "bayesilisk", "connector", "propose", str(source),
                                 "--enable-scenario-proposer", "--scenario-provider", "openai-compatible",
                                 "--scenario-base-url", f"http://127.0.0.1:{server.server_port}/v1",
                                 "--scenario-api-key-env", "TEST_CONNECTOR_MODEL_KEY", "--plan-output", str(plan)],
                                cwd=Path(__file__).resolve().parents[1], text=True, capture_output=True,
                                env={**os.environ, "TEST_CONNECTOR_MODEL_KEY": "test-credential"}, check=True)
    finally:
        server.shutdown()
        server.server_close()
        worker.join()
    assert len(json.loads(result.stdout)) == 1
    assert requests[0]["response_format"] == {"type": "json_object"}
    assert "1 admitted" in result.stderr
    prompt = requests[0]["messages"]
    assert "allowedFragmentIds" not in json.dumps(prompt)
    assert json.loads(prompt[1]["content"])["connectorInstructions"] == context["connectorInstructions"]
    compiled = json.loads(prompt[1]["content"])
    assert compiled["initiallyExecutableActions"] == ["create-fixture"]
    assert compiled["connectorActionGraph"] == context["connectorActionGraph"]
    saved = plan.read_text()
    assert "test-credential" not in result.stdout + result.stderr + saved
    assert json.loads(saved)["exploration"]["modelScenarioGeneration"]["acceptedCount"] == 1


def test_requested_provider_failure_is_reported(context: dict, monkeypatch) -> None:
    class Provider:
        requires_api_key = False

        def generate(self, *args, **kwargs):
            raise RuntimeError("provider unavailable")

    monkeypatch.setattr(exploration, "scenario_proposal_provider", lambda _: Provider())
    result = advance(None, source_context=context, runtime_config={"enableScenarioProposer": True})
    assert result["phase"] == "blocked"
    assert "provider unavailable" in result["nextAction"]


def test_source_rejection_blocks_before_model_or_execution(context: dict, monkeypatch) -> None:
    context["repositoryFacts"] = [{
        "source": "repository-scan", "title": "Invalid boundary", "invariantId": "booking.boundary",
        "routePattern": "https://production.example/bookings/{uid}", "params": [{"name": "uid"}],
        "availableActions": ["read"], "expectedBehavior": {"status": 404},
        "proposalRules": {"uid": [{"id": "missing", "value": "missing"}]},
    }]
    monkeypatch.setattr(exploration, "scenario_proposal_provider", lambda _: pytest.fail("model must not run"))
    result = advance(None, source_context=context, runtime_config={"enableScenarioProposer": True})
    assert result["phase"] == "blocked" and not result["sourceValidation"]["accepted"]
    assert result["proposals"] == []


def test_failed_replanning_does_not_reissue_previous_execution(context: dict, monkeypatch) -> None:
    class Provider:
        requires_api_key = False
        calls = 0

        def generate(self, *args, **kwargs):
            self.calls += 1
            if self.calls > 1:
                raise RuntimeError("replanning unavailable")
            return {"scenarios": [candidate()]}

    provider = Provider()
    monkeypatch.setattr(exploration, "scenario_proposal_provider", lambda _: provider)
    first = advance(None, source_context=context, runtime_config={"enableScenarioProposer": True})
    result = advance(first["state"], observed_context=_execute(first["proposals"][0]))
    assert result["phase"] == "blocked" and "replanning unavailable" in result["nextAction"]
    assert result["proposals"] == []


def test_validation_feedback_repairs_a_model_sequence(context: dict, monkeypatch) -> None:
    requests = []

    class Provider:
        requires_api_key = False

        def generate(self, prompt, config, api_key=None):
            requests.append(copy.deepcopy(prompt))
            assert config["scenarioResponseSchema"]["required"] == ["scenarios"]
            if len(requests) == 1:
                return {"scenarios": [candidate(["cancel", "read"])]}
            assert "unsatisfied typed dependencies" in prompt[-1]["content"]
            assert "executableActions" in prompt[-1]["content"]
            return {"scenarios": [candidate()]}

    monkeypatch.setattr(exploration, "scenario_proposal_provider", lambda _: Provider())
    result = exploration.explore_connector(context, runtime_config={"enableScenarioProposer": True, "scenarioMaxAttempts": 2})
    assert len(requests) == 2
    assert result["modelScenarioGeneration"]["acceptedCount"] == 1
    assert "error" not in result["modelScenarioGeneration"]


def test_zero_budget_never_calls_a_provider(context: dict, monkeypatch) -> None:
    def unexpected(*args):
        raise AssertionError("unexpected model call")

    monkeypatch.setattr(exploration, "scenario_proposal_provider", unexpected)
    assert exploration.explore_connector(context, runtime_config={"enableScenarioProposer": True}, limit=0)["proposals"] == []


def test_external_drafts_do_not_claim_configured_model_provenance(context: dict, monkeypatch) -> None:
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "1")
    monkeypatch.setattr(exploration, "scenario_proposal_provider", lambda _: pytest.fail("draft admission must not call a model"))
    result = exploration.explore_connector(context, drafts=[candidate()])
    provenance = result["proposals"][0]["modelProvenance"]
    assert provenance["source"] == provenance["provider"] == "external-draft"
    assert provenance["modelName"] == "unspecified" and provenance["promptHash"] is None
    assert not result["modelScenarioGeneration"]["enabled"]
    with pytest.raises(ValueError, match="separate operations"):
        exploration.explore_connector(context, drafts=[candidate()], runtime_config={"enableScenarioProposer": True})


def test_cli_rejects_an_invalid_draft_and_missing_provider(context: dict, tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    draft = tmp_path / "draft.json"
    source.write_text(json.dumps(context))
    draft.write_text(json.dumps({"scenarios": [candidate(["cancel", "read"])]}))
    command = [sys.executable, "-m", "bayesilisk", "connector", "propose", str(source)]
    rejected = subprocess.run([*command, "--draft-plan", str(draft)], capture_output=True, text=True)
    assert rejected.returncode == 1 and "no draft scenario passed" in rejected.stderr
    unavailable = subprocess.run([*command, "--enable-scenario-proposer", "--scenario-provider", "not-a-provider"],
                                 capture_output=True, text=True)
    assert unavailable.returncode == 1 and "unsupported-scenario-provider" in unavailable.stderr
