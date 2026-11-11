---
id: T-20261019-orgaos-pipeline
title: "Pipeline: percorrer varios orgaos"
status: ready
format_version: 3
profile: standard
effort: M
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-orgaos-config]
supersedes: (none)
touches_paths: [3-Etl/dags/scdp/pipeline.py, 3-Etl/dags/scdp/cli.py]
creates_paths: [tests/test_orgaos_pipeline.py]
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

# Pipeline: percorrer varios orgaos

> **Why:** RF11: cada orgao tem janelas e controle proprios.

## Goal

Executar o planejamento e a carga por orgao.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN dois orgaos com extrator falso WHEN a carga roda THEN cada orgao tem suas janelas em ctl_janela e nenhuma janela e lida duas vezes

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  REQUIRE_DB_TESTS=1 python -m pytest tests -q
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
    expected_duration_sec: 120
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

- Nao alterar a coluna orgao nem o schema de ctl_janela.

## Do-Not-Touch

- `3-Etl/dags/sql/schema.sql`

## Open Questions

(none — this task is fully specified)
