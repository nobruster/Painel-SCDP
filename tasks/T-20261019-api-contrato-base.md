---
id: T-20261019-api-contrato-base
title: "Script reproduzivel que consulta uma janela e conta viagens"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-r-testes-de-janela-no-codigo]
supersedes: (none)
touches_paths: []
creates_paths: [2-Scripts/testar_janelas_api.py, tests/test_testar_janelas_api.py]
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

# Script reproduzivel que consulta uma janela e conta viagens

> **Why:** Os testes de janela foram feitos a mao; o resultado precisa ser repetivel.

## Goal

Funcao contar(ida_de, ida_ate, ret_de, ret_ate) que usa o cliente da carga e devolve a contagem e as paginas.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN um cliente falso WHEN contar e chamada THEN devolve a contagem e o numero de paginas e propaga 400 como erro permanente

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  python -m pytest tests/test_testar_janelas_api.py -q
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

- Nao chamar a API real nos testes unitarios.

## Do-Not-Touch

- `3-Etl/dags/scdp/extracao.py`

## Open Questions

(none — this task is fully specified)
