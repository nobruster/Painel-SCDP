---
id: T-20261019-adr-canal-alerta
title: "ADR: canal de alerta"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-ferr-comparativo-alerta]
supersedes: (none)
touches_paths: []
creates_paths: [1-Documentos/adrs/0003-canal-de-alerta.md]
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

# ADR: canal de alerta

> **Why:** O modulo de alerta precisa saber o canal e onde fica o segredo.

## Goal

ADR com canal escolhido, onde o segredo mora e o que fazer se o canal falhar.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN o comparativo de alerta WHEN o ADR e escrito THEN ha Status proposta, Decisao, Alternativas rejeitadas e Consequencias

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  grep -qi "Status:" 1-Documentos/adrs/0003-canal-de-alerta.md && grep -qi "Alternativas rejeitadas" 1-Documentos/adrs/0003-canal-de-alerta.md && grep -qi "Consequencias" 1-Documentos/adrs/0003-canal-de-alerta.md
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

- Nao colocar URL de webhook real no documento.

## Do-Not-Touch

- `3-Etl`
- `2-Scripts`

## Open Questions

(none — this task is fully specified)
