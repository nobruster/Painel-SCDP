---
id: T-20261019-r-dicionario-de-dados
title: "Ler o dicionario oficial e mapear para a API"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-r-listas-de-orgaos]
supersedes: (none)
touches_paths: []
creates_paths: []
source_note: "1-Documentos/dicionario-de-dados-viagens.md"
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

# Ler o dicionario oficial e mapear para a API

> **Why:** Descobrir o que a API nao expoe (trechos, passagens, pagamentos, outros gastos).

## Goal

Dicionario dos 4 arquivos e correspondencia com /viagens.

## Context

TAREFA RETROATIVA: o trabalho ja foi feito; este contrato registra e verifica. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN o dicionario oficial WHEN ele e comparado com a API THEN ha as secoes dos 4 arquivos e a correspondencia com a API

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  grep -qF -- "## Arquivo Viagem" 1-Documentos/dicionario-de-dados-viagens.md && grep -qF -- "## Arquivo Trecho" 1-Documentos/dicionario-de-dados-viagens.md && grep -qF -- "## Correspondência com a API" 1-Documentos/dicionario-de-dados-viagens.md
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
