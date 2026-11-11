# Runbook: validar a carga completa desde 2025

Objetivo: provar, no banco real, que a carga completa leu todas as janelas desde 2025-01 e que cada janela conferiu (`qtd_api = qtd_carregada`). O gate e `2-Scripts/validar_carga_completa.py`. Somente leitura: nao altera dados e nao chama a API.

## Criterio de aceite

`CARGA=OK` com exit 0, ou seja, para o orgao configurado:
- toda janela planejada desde `--desde` (padrao `2025-01`) existe em `ctl_janela` (`sem_registro 0`);
- todas estao com status OK (`fora_de_ok 0`);
- todas tem `qtd_api = qtd_carregada` (`qtd_diferente 0`).

O numero de janelas planejadas cresce 13 por mes: eram 312 em out/2026 e sao 325 em nov/2026. O criterio e `planejadas = registradas`, nao um numero fixo.

## Passo a passo

1. Rodar a carga completa (leva horas; na producao a DAG `scdp_carga_completa` faz isso nos dias 1, 11 e 21 as 03:30):
   `python -I 3-Etl/dags/carga_viagens.py --modo completo --desde 2025-01`
2. Rodar o gate de janelas:
   `python -I 2-Scripts/validar_carga_completa.py`
3. Rodar o gate de reconciliacao entre camadas:
   `python -I 2-Scripts/verificar_reconciliacao.py`
4. Conferir `SELECT * FROM staging.vw_ctl_erros_abertos;` e `... vw_ctl_pendencias;` (ambas vazias).

Na DAG completa, os passos 2 e 3 sao as tarefas `validar_janelas` e `reconciliar`.

## Saidas possiveis

| Saida | Significado |
|---|---|
| `CARGA=OK` | criterio atendido |
| `CARGA=DIVERGENTE` | faltam janelas, ha janela fora de OK ou com `qtd_api` diferente de `qtd_carregada`; o script lista ate 20 por motivo |
| `CARGA=NAO_MEDIDO` | `ctl_janela` vazia, nada foi lido; nao e aprovacao |
| `CARGA=ERRO (...)` | falha ao medir (configuracao ou conexao) |

Se DIVERGENTE: janelas sem registro ou fora de OK, rodar de novo o passo 1 (a carga relê as pendentes e as com erro) e repetir o gate; janela com quantidades diferentes, rodar `--modo completo --desde AAAA-MM` do mes dela e, persistindo, seguir `MANUAL-recuperacao.md`. Nao apague dados da staging.

## Evidencia real

Executado em 2026-11-11 (18:08, horario local) contra o banco de producao, em modo leitura:

```
python -I 2-Scripts/validar_carga_completa.py
planejadas                   325
registradas                  325
sem_registro                 0
fora_de_ok                   0
qtd_diferente                0
CARGA=OK            (exit 0)

python -I 2-Scripts/verificar_reconciliacao.py
stg 3855 | int 3855 | fct 3855 | obt 3855
total_nulo 0 | total_nao_fecha 0 | outros_gastos_negativo 0 | outros_gastos_positivo 63
soma_total_int 21495889.58 | soma_total_fct 21495889.58
RECONCILIACAO=OK    (exit 0)
```

Leitura: em nov/2026 sao 325 janelas planejadas (os 312 de out/2026 mais 13 do mes), todas registradas, em OK e conferidas; as quatro camadas tem 3.855 viagens e a soma do total fecha. O criterio de aceite esta atendido nesta data. Esta evidencia reflete o estado do banco no momento da execucao; repita os comandos para uma nova data. A ultima carga completa registrada foi a de 11/11 as 03:31.
