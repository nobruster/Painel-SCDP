---
id: T-20261019-ferr-criterios
title: "Definir criterios para escolher ferramentas"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-req-nao-funcionais-painel]
supersedes: (none)
touches_paths: []
creates_paths: [1-Documentos/ferramentas/criterios.md]
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

# Definir criterios para escolher ferramentas

> **Why:** Escolher ferramenta sem criterio e escolher por gosto.

## Goal

Criterios com peso: custo, licenca, conexao PostgreSQL, hospedagem, LGPD, curva de aprendizado, manutencao.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN os requisitos nao funcionais WHEN os criterios sao definidos THEN cada criterio tem peso de 1 a 5 e justificativa

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  grep -qi "custo" 1-Documentos/ferramentas/criterios.md && grep -qi "licenca" 1-Documentos/ferramentas/criterios.md && grep -qi "postgres" 1-Documentos/ferramentas/criterios.md && grep -qi "lgpd" 1-Documentos/ferramentas/criterios.md && grep -qi "peso" 1-Documentos/ferramentas/criterios.md
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

- Nao pontuar ferramenta neste documento.

## Do-Not-Touch

- `3-Etl`
- `2-Scripts`

## Open Questions

(none — this task is fully specified)
