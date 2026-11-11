---
id: T-20261019-req-perguntas-de-negocio
title: "Levantar as perguntas de negocio que o painel responde"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-r-resultado-varredura-2026]
supersedes: (none)
touches_paths: []
creates_paths: [1-Documentos/requisitos/perguntas-de-negocio.md]
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

# Levantar as perguntas de negocio que o painel responde

> **Why:** Sem perguntas explicitas o painel vira um amontoado de graficos.

## Goal

Lista numerada P-1.. de perguntas (quanto se gasta, onde, com quem, quando), cada uma com o campo que a responde.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN o PRD, o dicionario de dados e o CLAUDE.md WHEN as perguntas de negocio sao extraidas THEN ha ao menos 8 perguntas P-n, cada uma citando campo ou coluna e marcada como a validar com o usuario

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  test "$(grep -c "^## P-" 1-Documentos/requisitos/perguntas-de-negocio.md)" -ge 8
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

- Nao inventar campo que a API nao devolve (sem trechos, passagens por viagem, destinos).

## Do-Not-Touch

- `3-Etl`
- `2-Scripts`

## Open Questions

(none — this task is fully specified)
