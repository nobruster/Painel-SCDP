---
id: T-20261019-validar-carga-script
title: "Script do gate de janelas"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-r-controle-por-janela]
supersedes: (none)
touches_paths: []
creates_paths: [2-Scripts/validar_carga_completa.py, tests/test_validar_carga.py]
source_note: "PRD.md"
created: "2026-10-19T00:00:00Z"
tags: []
owner: (none)
priority: P2
severity: feature
due_date: (none)
precondition: (none)
blocked_reason: (none)
security_class: (none)
source_action_item: (none)
tracker_ref: (none)
execution_backend: claude
signed_off: false
signed_off_by: (none)
signed_off_at: (none)
accepted: false
accepted_by: (none)
accepted_at: (none)
---

# Script do gate de janelas

> **Why:** A meta de 100% das janelas OK nao tem verificador.

## Goal

Ler ctl_janela e devolver CARGA=OK|DIVERGENTE|NAO_MEDIDO|ERRO.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN ctl_janela vazia, ou com janela ERRO, ou com qtd_api diferente de qtd_carregada WHEN o gate roda THEN vazia devolve NAO_MEDIDO, divergencia devolve DIVERGENTE com a lista, tudo certo devolve OK

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  REQUIRE_DB_TESTS=1 python -m pytest tests/test_validar_carga.py -q
}

```

## Validation Card

```yaml
success_criteria:
  - id: eval_1
    description: "verificacao da tarefa"
    runnable: bash
    check_type: deterministic
    verifies: [B-1]
    terminal: true
    expected_duration_sec: 60
retry_policy:
  max_iterations: 15
  circuit_breaker_no_progress: 3
  on_terminal_failure: park_with_context
agent_contract:
  version: 2
  read: [intent, behavior, contract, guardrails]
  produce: [code, tests]
  required_tools: [git, bash]
  timeout_minutes: 30
  sandbox_type: host
  output_artifacts: []
  mcp_dependencies: []
  emit: [pass, fail, retry_with_reason, parked_with_context]
  backend_metadata: {}
```

## Exit Check

```bash
eval_1
```

## Rollback Plan

Revert only the declared write surface and park the task with context.

## Observability Hooks

(none — no runtime observability required)

## Anti-Patterns

- Zero janelas nunca e OK.

## Do-Not-Touch

- `3-Etl/dags/scdp/reconciliacao.py`

## Open Questions

(none — this task is fully specified)
