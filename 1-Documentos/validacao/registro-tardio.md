# Runbook: exercitar registro tardio

Objetivo: confirmar, com dados reais, que a carga detecta uma viagem antiga que o portal publicou com atraso (RF8, antes testado so em simulacao). Somente leitura; nao insira nem altere dados de producao para forcar um caso.

## O que e TARDIO

O portal pode publicar uma viagem muito depois do inicio dela (a tela de consulta tem cerca de 45 dias de defasagem). Uma viagem e TARDIA quando entra na staging pela primeira vez, em janela que ja estava OK, e o mes de ida e mais antigo que os ultimos 3 meses (`meses_recentes`). A diaria so relê os ultimos 3 meses; quem encontra esse caso e a carga completa (dias 1, 11 e 21), que relê todas as janelas. No log da carga a linha da janela sai com a marca `TARDIO` e o resumo final traz `tardios=N`.

## Como a vw_ctl_tardios detecta

`staging.vw_ctl_tardios` junta `stg_viagem` e `int_viagem` e lista as viagens que cumprem as tres condicoes:
1. `data_inicio` anterior ao primeiro dia do mes de 3 meses atras;
2. `carregado_em` nas ultimas 48 horas;
3. `carregado_em` mais de 1 dia depois da primeira execucao registrada em `ctl_execucao` (exclui a carga inicial).

Colunas: `id`, `data_inicio`, `data_fim`, `janela_ida`, `janela_retorno`, `carregado_em`. A view reflete uma janela de 2 dias: o que a carga encontrou em cada execucao recente.

## Como exercitar

1. Rodar `python -I 3-Etl/dags/carga_viagens.py --modo completo --desde 2025-01` (ou aguardar a DAG `scdp_carga_completa`).
2. Procurar `TARDIO` no log da execucao e `tardios=` na ultima linha de resumo.
3. Consultar `SELECT count(*) FROM staging.vw_ctl_tardios;` e, para o detalhe, `SELECT * FROM staging.vw_ctl_tardios ORDER BY carregado_em DESC;`.
4. Conferir que a mesma viagem existe na intermediaria e na analitica (`int_viagem`, `fct_viagem`) e que o gate `python -I 2-Scripts/verificar_reconciliacao.py` continua `RECONCILIACAO=OK`.

## Criterio de aceite

- A consulta a `vw_ctl_tardios` executa sem erro, e toda linha tem `data_inicio` com mais de 3 meses e `carregado_em` dentro das ultimas 48 horas.
- Quando a view tem linhas, cada uma tambem esta na intermediaria e na analitica, e a reconciliacao fecha (`RECONCILIACAO=OK`).
- Contagem zero e resultado valido: significa que o portal nao publicou nada com atraso na janela. O registro tardio so fica provado por um caso real quando a contagem e maior que zero.

## Evidencia real

Consulta de leitura executada em 2026-11-11 contra o banco de producao:

```
SELECT count(*) FROM staging.vw_ctl_tardios;   ->  38
```

As 38 viagens tem `data_inicio` entre 2025-09-01 e 2026-07-30 e `carregado_em` entre 03:31:11 e 03:32:59 de 2026-11-11, o intervalo da carga completa de 11/11 (03:30). Ou seja, a carga completa encontrou 38 viagens antigas que a diaria nao relê, e a view as registrou como TARDIO. A reconciliacao no mesmo dia: `RECONCILIACAO=OK` com 3.855 viagens em staging, intermediaria, fato e OBT.

Ressalva: a view deteta por data de carga, nao prova sozinha que o portal publicou com atraso; parte dessas 38 pode ser viagem que mudou de janela ou foi relida apos a carga inicial de 19/10/2026. Para confirmar a causa de um caso, compare `janela_ida`/`janela_retorno` com `ctl_janela` e o log da execucao.
