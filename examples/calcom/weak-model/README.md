# Cal.com Weak-Model Evidence

This directory stores local scenario-proposer evidence for the Cal.com case
study.

Current artifact:

- `qwen2.5-coder-3b-source-report.json`

Summary:

- Provider: Ollama
- Model: `qwen2.5-coder:3b`
- Raw model proposals: `3`
- Accepted by Bayesilisk verifier: `0`
- Rejected by Bayesilisk verifier: `3`

The model proposals were rejected because they did not match the selected
finite-state verifier context. This supports the Bayesilisk boundary: local
models may propose scenarios, but deterministic verifier gates decide whether a
proposal is valid and whether observed evidence is a failure.
