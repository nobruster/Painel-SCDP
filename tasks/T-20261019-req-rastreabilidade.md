---
id: T-20261019-req-rastreabilidade
title: "Matriz requisito x coluna x camada com teste"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-req-kpis, T-20261019-req-filtros-e-recortes]
supersedes: (none)
touches_paths: []
creates_paths: [1-Documentos/requisitos/rastreabilidade.csv, tests/test_rastreabilidade.py]
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

# Matriz requisito x coluna x camada com teste

> **Why:** Garante que todo KPI e filtro tem coluna real por tras.

## Goal

CSV (requisito, coluna, camada) e teste que confere cada coluna no schema.sql.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN kpis.md, filtros.md e schema.sql WHEN o teste de rastreabilidade roda THEN toda coluna citada existe em schema.sql e nenhum requisito fica sem linha

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  python -m pytest tests/test_rastreabilidade.py -q
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

- Nao criar coluna no schema para fazer o teste passar.

## Do-Not-Touch

- `3-Etl/dags/sql/schema.sql`

## Open Questions

(none — this task is fully specified)
