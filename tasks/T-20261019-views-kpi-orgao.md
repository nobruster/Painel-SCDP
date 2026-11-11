---
id: T-20261019-views-kpi-orgao
title: "View vw_kpi_orgao"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-views-kpi-mes]
supersedes: (none)
touches_paths: [3-Etl/dags/sql/schema.sql]
creates_paths: [tests/test_view_kpi_orgao.py]
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

# View vw_kpi_orgao

> **Why:** Necessaria assim que houver mais de um orgao.

## Goal

View por orgao e ano_mes.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN viagens de dois orgaos WHEN a view e consultada THEN cada orgao soma o proprio total e a soma dos orgaos bate com a fct_viagem

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  REQUIRE_DB_TESTS=1 python -m pytest tests/test_view_kpi_orgao.py -q
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

- Nao expor beneficiario.

## Do-Not-Touch

- `3-Etl/dags/scdp/transformacao.py`

## Open Questions

(none — this task is fully specified)
