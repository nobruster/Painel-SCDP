---
id: T-20261019-ferr-comparativo-alerta
title: "Levantar e comparar canais de alerta"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-ferr-criterios]
supersedes: (none)
touches_paths: []
creates_paths: [1-Documentos/ferramentas/comparativo-alerta.md]
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

# Levantar e comparar canais de alerta

> **Why:** O alerta depende do que o orgao permite usar.

## Goal

Comparar Teams, Slack, e-mail SMTP e o e-mail nativo do Airflow quanto a custo, segredo e confiabilidade.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN os criterios WHEN os canais sao comparados THEN cada canal tem como o segredo e guardado e o que acontece se o canal cair

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  grep -qi "teams" 1-Documentos/ferramentas/comparativo-alerta.md && grep -qi "slack" 1-Documentos/ferramentas/comparativo-alerta.md && grep -qi "smtp" 1-Documentos/ferramentas/comparativo-alerta.md && grep -qi "airflow" 1-Documentos/ferramentas/comparativo-alerta.md && grep -qi "segredo" 1-Documentos/ferramentas/comparativo-alerta.md
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

- Nao assumir que o webhook e permitido no orgao; marcar como a confirmar.

## Do-Not-Touch

- `3-Etl`
- `2-Scripts`

## Open Questions

(none — this task is fully specified)
