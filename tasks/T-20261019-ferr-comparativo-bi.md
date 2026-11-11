---
id: T-20261019-ferr-comparativo-bi
title: "Levantar e comparar ferramentas de BI"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-ferr-criterios, T-20261019-req-kpis]
supersedes: (none)
touches_paths: []
creates_paths: [1-Documentos/ferramentas/comparativo-bi.md]
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

# Levantar e comparar ferramentas de BI

> **Why:** O PRD cita Power BI, Metabase e Pentaho sem comparar.

## Goal

Matriz Power BI x Metabase x Superset x Streamlit contra cada criterio, com fonte de cada afirmacao.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN os criterios WHEN as ferramentas sao comparadas THEN toda ferramenta tem nota em todo criterio e link ou fonte; nada fica sem nota

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  grep -qi "power bi" 1-Documentos/ferramentas/comparativo-bi.md && grep -qi "metabase" 1-Documentos/ferramentas/comparativo-bi.md && grep -qi "superset" 1-Documentos/ferramentas/comparativo-bi.md && grep -qi "streamlit" 1-Documentos/ferramentas/comparativo-bi.md && grep -qi "fonte" 1-Documentos/ferramentas/comparativo-bi.md
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
    expected_duration_sec: 10
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

- Nao recomendar sem citar o criterio decisivo.

## Do-Not-Touch

- `3-Etl`
- `2-Scripts`

## Open Questions

(none — this task is fully specified)
