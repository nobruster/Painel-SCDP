---
id: T-20261019-r-escopo-orgaos-descoberto
title: "Descobrir que codigoOrgao filtra a entidade e nao o ministerio"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-r-enums-ug-e-sigilo]
supersedes: (none)
touches_paths: []
creates_paths: []
source_note: "1-Documentos/PRD.md"
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

# Descobrir que codigoOrgao filtra a entidade e nao o ministerio

> **Why:** Consultar so 33000 perde o INSS.

## Goal

Comparar 33000, 37202 e 33206 em agosto; Marinha x Defesa.

## Context

TAREFA RETROATIVA: o trabalho ja foi feito; este contrato registra e verifica. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN agosto/2026 WHEN cada orgao e consultado THEN 142, 1.265 e 22 viagens; Defesa 52000 so 1 contra 7 da Marinha 52131

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  grep -qF -- "37202" 1-Documentos/PRD.md && grep -qF -- "33206" 1-Documentos/PRD.md && grep -qF -- "1.265" 1-Documentos/PRD.md
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

- Tarefa retroativa, registra e verifica o que ja foi feito, nao reescrever o artefato.

## Do-Not-Touch

- `darkfactory-template`

## Open Questions

(none — this task is fully specified)
