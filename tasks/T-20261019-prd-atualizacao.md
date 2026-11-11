---
id: T-20261019-prd-atualizacao
title: "Atualizar PRD e README com o estado real"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-adr-escopo-orgaos, T-20261019-adr-beneficiario-lgpd, T-20261019-orgaos-pipeline, T-20261019-janela-queda-aviso, T-20261019-alerta-dag-completa, T-20261019-validar-carga-dag, T-20261019-painel-especificacao]
supersedes: (none)
touches_paths: [1-Documentos/PRD.md, README.md]
creates_paths: []
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

# Atualizar PRD e README com o estado real

> **Why:** RF11 e RF12 constam como pendentes e o escopo do painel mudou.

## Goal

PRD e README refletem o que foi entregue e as decisoes dos ADRs.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN os ADRs e o codigo WHEN os documentos sao atualizados THEN RF11 e RF12 deixam de ser Pendente e cada decisao cita seu ADR

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  ! grep -n "RF11.*Pendente" 1-Documentos/PRD.md && grep -q "adrs/0001" 1-Documentos/PRD.md
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

- Nao marcar como implementado o que nao esta no codigo.

## Do-Not-Touch

- `3-Etl`

## Open Questions

(none — this task is fully specified)
