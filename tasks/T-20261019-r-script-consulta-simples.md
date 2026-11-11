---
id: T-20261019-r-script-consulta-simples
title: "Criar o script de busca de viagens por intervalo de datas"
status: ready
format_version: 3
profile: standard
effort: XS
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-r-colecao-postman]
supersedes: (none)
touches_paths: []
creates_paths: []
source_note: "2-Scripts/consulta_viagens.py"
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

# Criar o script de busca de viagens por intervalo de datas

> **Why:** Primeiro contato real com a API: buscar um intervalo e paginar ate [].

## Goal

consulta_viagens.py le o .env, pagina de 15 em 15 e imprime id, datas, nome e valor.

## Context

TAREFA RETROATIVA: o trabalho ja foi feito; este contrato registra e verifica. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN janela de 01/09 a 30/09/2026 e o orgao do .env WHEN o script roda THEN pagina ate a lista vazia, com pausa de 0,7 s entre chamadas

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  python -m py_compile 2-Scripts/consulta_viagens.py && grep -q dataIdaDe 2-Scripts/consulta_viagens.py && grep -q 'time.sleep' 2-Scripts/consulta_viagens.py
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
