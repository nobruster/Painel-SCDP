---
id: T-20261019-validar-carga-dag
title: "Ligar o gate de janelas na DAG completa"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-validar-carga-script, T-20261019-alerta-dag-completa]
supersedes: (none)
touches_paths: [3-Etl/dags/dag_carga_completa.py]
creates_paths: [tests/test_validar_carga_dag.py]
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

# Ligar o gate de janelas na DAG completa

> **Why:** A carga completa e a que deve fechar 100% das janelas.

## Goal

Tarefa validar_janelas apos a reconciliacao, sem retry, com o comando montado na propria DAG a partir de PAINEL_SCDP_HOME e PAINEL_SCDP_PYTHON.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN a DAG completa WHEN o texto do arquivo e inspecionado THEN validar_janelas existe, vem depois de reconciliar e tem retries=0

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  python -m pytest tests/test_validar_carga_dag.py tests/test_cli_e_dags.py -q
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
    expected_duration_sec: 20
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

- Nao mudar a agenda.

## Do-Not-Touch

- `3-Etl/dags/scdp/carga.py`

## Open Questions

(none — this task is fully specified)
