---
id: T-20261019-runbook-registro-tardio
title: "Runbook: exercitar registro tardio"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-validar-carga-script]
supersedes: (none)
touches_paths: []
creates_paths: [1-Documentos/validacao/registro-tardio.md]
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

# Runbook: exercitar registro tardio

> **Why:** RF8 so foi testado em simulacao.

## Goal

Como provocar e confirmar um TARDIO em vw_ctl_tardios.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN o modo completo WHEN o runbook e escrito THEN cita vw_ctl_tardios, TARDIO e o criterio de sucesso

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  grep -qi "vw_ctl_tardios" 1-Documentos/validacao/registro-tardio.md && grep -qi "TARDIO" 1-Documentos/validacao/registro-tardio.md && grep -qi "criterio" 1-Documentos/validacao/registro-tardio.md
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

- Nao apagar dado de producao no exemplo.

## Do-Not-Touch

- `3-Etl`
- `2-Scripts`

## Open Questions

(none — this task is fully specified)
