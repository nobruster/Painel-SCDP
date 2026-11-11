---
id: T-20261019-alerta-modulo
title: "Modulo de alerta (mensagem e envio)"
status: ready
format_version: 3
profile: standard
effort: S
budget_iterations: 15
agent: any
parent: (none)
depends_on: [T-20261019-adr-canal-alerta, T-20261019-r-gate-na-dag]
supersedes: (none)
touches_paths: []
creates_paths: [3-Etl/dags/scdp/alerta.py, tests/test_alerta.py]
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

# Modulo de alerta (mensagem e envio)

> **Why:** Falha hoje so vira codigo de saida.

## Goal

Montar mensagem sem segredos e enviar ao canal do ADR quando configurado.

## Context

Tarefa nova do plano de entrega. Ler o CLAUDE.md do projeto antes de escrever.

## Behavior

- **B-1** — GIVEN um veredito diferente de OK com motivos WHEN o alerta e montado e enviado THEN a mensagem traz veredito e motivos, segredos saem como ***, e sem configuracao devolve NAO_CONFIGURADO sem rede

## Success Criteria

```bash
# eval_1: verificacao da tarefa
eval_1() {
  python -m pytest tests/test_alerta.py -q
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

- Nao logar chave da API nem senha do banco.

## Do-Not-Touch

- `3-Etl/dags/scdp/extracao.py`

## Open Questions

(none — this task is fully specified)
