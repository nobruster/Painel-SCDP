# Projeto SCDP Viagens: tarefas

O trabalho já feito está dividido em 66 tarefas pequenas (F0 a F7). Cada uma tem um arquivo `tasks/T-20261019-<tarefa>.md` (contrato Task-Spec com o comportamento esperado e o comando que o verifica) e o artefato onde o resultado ficou salvo. Outras 38 tarefas (G1 a G6) levam o projeto à entrega: requisitos e ferramentas do painel, alerta, vários órgãos, views de consumo e manuais. A coluna Status abaixo vem da execução do comando de verificação de cada tarefa em 11/11/2026.

## F0. Descoberta da API (6)

| Tarefa | Onde ficou |
|---|---|
| [Obter a chave e guardar no `.env` fora do git](../tasks/T-20261019-r-env-e-chave.md) | `.env.example` |
| [Baixar a spec Swagger (109 endpoints)](../tasks/T-20261019-r-spec-swagger.md) | `1-Documentos/referencia_api.md` |
| [Mapear os 3 endpoints de viagens](../tasks/T-20261019-r-endpoints-de-viagens.md) | `1-Documentos/PRD.md` |
| [Criar a coleção do Postman](../tasks/T-20261019-r-colecao-postman.md) | `2-Scripts/postman/postman_collection.json`, `2-Scripts/postman/postman_environment.json` |
| [Criar o script de busca por intervalo (`consulta_viagens.py`)](../tasks/T-20261019-r-script-consulta-simples.md) | `2-Scripts/consulta_viagens.py` |
| [Testar a autenticação](../tasks/T-20261019-r-teste-autenticacao.md) | `1-Documentos/perguntas-dono-da-api.md` |

## F1. Testes de janela de datas (cada teste é uma tarefa) (13)

| Tarefa | Onde ficou |
|---|---|
| [Dentro do mês: 142 viagens em 10 páginas](../tasks/T-20261019-r-jan-dentro-do-mes.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [Fim da paginação](../tasks/T-20261019-r-jan-fim-da-paginacao.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [Ida em março com retorno em março, abril e junho: 312, 18 e 3 viagens](../tasks/T-20261019-r-jan-mes-mais-1-e-mais-3.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [Retorno até 12 meses depois (viagem mais longa: 181 dias)](../tasks/T-20261019-r-jan-mes-mais-12.md) | `1-Documentos/perguntas-dono-da-api.md`, `1-Documentos/PRD.md` |
| [Limite de 1 mês por par de datas (31 dias passa, 32 dá 400)](../tasks/T-20261019-r-jan-limite-de-1-mes.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [Janela menor que um mês: 94 viagens](../tasks/T-20261019-r-jan-menor-que-um-mes.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [Dia único: 41 viagens em 04/03 e 0 em 03/03](../tasks/T-20261019-r-jan-dia-unico.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [`Ate` anterior a `De`: devolve vazio, sem erro](../tasks/T-20261019-r-jan-ate-antes-de-de.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [Parâmetros obrigatórios](../tasks/T-20261019-r-jan-parametros-obrigatorios.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [Anomalias (retorno antes da ida, retorno em 2028)](../tasks/T-20261019-r-jan-anomalias.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [Repetibilidade (mesmos 1.460 ids nas duas varreduras)](../tasks/T-20261019-r-jan-repetibilidade.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [Detalhe por id, com 504 frequente](../tasks/T-20261019-r-jan-detalhe-por-id.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [O planejador de janelas coberto em código](../tasks/T-20261019-r-testes-de-janela-no-codigo.md) | `3-Etl/dags/scdp/janelas.py` |

## F2. Varredura e dados (6)

| Tarefa | Onde ficou |
|---|---|
| [Script `varredura_2026.py`](../tasks/T-20261019-r-script-varredura-2026.md) | `2-Scripts/varredura_2026.py` |
| [Resultado: 1.460 viagens](../tasks/T-20261019-r-resultado-varredura-2026.md) | `1-Documentos/PRD.md` |
| [Distância entre ida e retorno](../tasks/T-20261019-r-distancia-ida-retorno.md) | `1-Documentos/PRD.md` |
| [Integridade dos dados](../tasks/T-20261019-r-integridade-dos-dados.md) | `1-Documentos/PRD.md` |
| [Fórmula do valor total](../tasks/T-20261019-r-regra-do-valor-total.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [Valores possíveis, unidades gestoras e viagens sigilosas](../tasks/T-20261019-r-enums-ug-e-sigilo.md) | `1-Documentos/perguntas-dono-da-api.md` |

## F3. Escopo e documentação (8)

| Tarefa | Onde ficou |
|---|---|
| [`codigoOrgao` filtra a entidade, não o ministério (INSS 1.265 contra 142)](../tasks/T-20261019-r-escopo-orgaos-descoberto.md) | `1-Documentos/PRD.md` |
| [Código `308819`](../tasks/T-20261019-r-codigo-308819.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [Listas de órgãos SIAFI e SIAPE](../tasks/T-20261019-r-listas-de-orgaos.md) | `1-Documentos/referencia/orgaos_siafi.csv`, `1-Documentos/referencia/orgaos_siape.csv` |
| [Dicionário de dados](../tasks/T-20261019-r-dicionario-de-dados.md) | `1-Documentos/dicionario-de-dados-viagens.md` |
| [Limites de requisição](../tasks/T-20261019-r-limites-de-uso.md) | `1-Documentos/PRD.md` |
| [Download em lote](../tasks/T-20261019-r-avaliacao-download-em-lote.md) | `1-Documentos/PRD.md` |
| [Perguntas ao dono da API](../tasks/T-20261019-r-perguntas-ao-dono-da-api.md) | `1-Documentos/perguntas-dono-da-api.md` |
| [PRD v0.1](../tasks/T-20261019-r-prd-v01.md) | `1-Documentos/PRD.md` |

## F4. Modelo de dados (6)

| Tarefa | Onde ficou |
|---|---|
| [Staging](../tasks/T-20261019-r-schema-staging.md) | `3-Etl/dags/sql/schema.sql` |
| [Tabelas de controle](../tasks/T-20261019-r-schema-controle.md) | `3-Etl/dags/sql/schema.sql` |
| [Camada intermediária](../tasks/T-20261019-r-schema-intermediaria.md) | `3-Etl/dags/sql/schema.sql` |
| [Funções tolerantes a dado sujo](../tasks/T-20261019-r-conversoes-tolerantes.md) | `3-Etl/dags/sql/schema.sql` |
| [Camada analítica](../tasks/T-20261019-r-schema-analitica.md) | `3-Etl/dags/sql/schema.sql` |
| [Schema versionado por hash](../tasks/T-20261019-r-schema-versionado.md) | `3-Etl/dags/sql/schema.sql` |

## F5. Código da carga (17)

| Tarefa | Onde ficou |
|---|---|
| [Configuração](../tasks/T-20261019-r-config.md) | `3-Etl/dags/scdp/config.py` |
| [Tentativas e espera para 504 e 429](../tasks/T-20261019-r-extracao-retry.md) | `3-Etl/dags/scdp/extracao.py` |
| [Paginação com trava contra loop](../tasks/T-20261019-r-extracao-paginacao.md) | `3-Etl/dags/scdp/extracao.py` |
| [Não vazar a chave](../tasks/T-20261019-r-extracao-seguranca.md) | `3-Etl/dags/scdp/extracao.py` |
| [Ritmo conforme o limite do horário](../tasks/T-20261019-r-extracao-ritmo.md) | `3-Etl/dags/scdp/extracao.py` |
| [Planejamento de janelas](../tasks/T-20261019-r-janelas-planejamento.md) | `3-Etl/dags/scdp/janelas.py` |
| [Modos diário e completo](../tasks/T-20261019-r-janelas-modos.md) | `3-Etl/dags/scdp/janelas.py` |
| [Retomada](../tasks/T-20261019-r-janelas-retomada.md) | `3-Etl/dags/scdp/janelas.py`, `3-Etl/dags/scdp/pipeline.py` |
| [Staging por hash](../tasks/T-20261019-r-staging-hash-upsert.md) | `3-Etl/dags/scdp/transformacao.py` |
| [Controle por janela](../tasks/T-20261019-r-controle-por-janela.md) | `3-Etl/dags/scdp/controle.py`, `3-Etl/dags/scdp/pipeline.py` |
| [Registro de erros](../tasks/T-20261019-r-registro-de-erros.md) | `3-Etl/dags/scdp/erros.py`, `3-Etl/dags/scdp/controle.py` |
| [Camada intermediária incremental](../tasks/T-20261019-r-silver-incremental.md) | `3-Etl/dags/scdp/transformacao.py` |
| [Camada analítica incremental](../tasks/T-20261019-r-gold-incremental.md) | `3-Etl/dags/scdp/transformacao.py` |
| [Trava de execução](../tasks/T-20261019-r-trava-de-execucao.md) | `3-Etl/dags/scdp/carga.py`, `3-Etl/dags/scdp/pipeline.py` |
| [CLI](../tasks/T-20261019-r-cli.md) | `3-Etl/dags/scdp/cli.py`, `3-Etl/dags/carga_viagens.py` |
| [Views de observabilidade](../tasks/T-20261019-r-views-de-observabilidade.md) | `3-Etl/dags/sql/schema.sql` |
| [Mascaramento de segredos](../tasks/T-20261019-r-seguranca-de-segredos.md) | `3-Etl/dags/scdp/config.py`, `3-Etl/dags/scdp/erros.py` |

## F6. Airflow (4)

| Tarefa | Onde ficou |
|---|---|
| [`dag_util`](../tasks/T-20261019-r-dag-util.md) | `3-Etl/dags/scdp/dag_util.py` |
| [DAG diária](../tasks/T-20261019-r-dag-diaria.md) | `3-Etl/dags/dag_carga_diaria.py` |
| [DAG completa](../tasks/T-20261019-r-dag-completa.md) | `3-Etl/dags/dag_carga_completa.py` |
| [`.airflowignore`](../tasks/T-20261019-r-airflowignore.md) | `3-Etl/dags/.airflowignore` |

## F7. Qualidade (6)

| Tarefa | Onde ficou |
|---|---|
| [CI](../tasks/T-20261019-r-ci-github.md) | `.github/workflows/ci.yml` |
| [Revisão independente 1](../tasks/T-20261019-r-revisao-independente-1.md) | `1-Documentos/PRD.md` |
| [Revisão independente 2](../tasks/T-20261019-r-revisao-independente-2.md) | `1-Documentos/PRD.md` |
| [Gate de reconciliação](../tasks/T-20261019-r-gate-de-reconciliacao.md) | `3-Etl/dags/scdp/reconciliacao.py`, `2-Scripts/verificar_reconciliacao.py` |
| [Gate ligado nas DAGs](../tasks/T-20261019-r-gate-na-dag.md) | `3-Etl/dags/dag_carga_diaria.py`, `3-Etl/dags/dag_carga_completa.py` |
| [Validação contra o `darkfactory-template`](../tasks/T-20261019-r-validacao-contra-darkfactory.md) | `1-Documentos/PRD.md` |

## G1. Requisitos do painel (5)

| Tarefa | Status | Onde ficou |
|---|---|---|
| [Levantar as perguntas de negocio que o painel responde](../tasks/T-20261019-req-perguntas-de-negocio.md) | Cancelada (painel fora do escopo) | `1-Documentos/requisitos/perguntas-de-negocio.md` |
| [Definir os KPIs com formula e fonte](../tasks/T-20261019-req-kpis.md) | Cancelada (painel fora do escopo) | `1-Documentos/requisitos/kpis.md` |
| [Definir filtros e recortes do painel](../tasks/T-20261019-req-filtros-e-recortes.md) | Cancelada (painel fora do escopo) | `1-Documentos/requisitos/filtros.md` |
| [Levantar requisitos nao funcionais do painel](../tasks/T-20261019-req-nao-funcionais-painel.md) | Cancelada (painel fora do escopo) | `1-Documentos/requisitos/nao-funcionais-painel.md` |
| [Matriz requisito x coluna x camada com teste](../tasks/T-20261019-req-rastreabilidade.md) | Cancelada (painel fora do escopo) | `1-Documentos/requisitos/rastreabilidade.csv`, `tests/test_rastreabilidade.py` |

## G2. Ferramentas e decisoes (8)

| Tarefa | Status | Onde ficou |
|---|---|---|
| [Definir criterios para escolher ferramentas](../tasks/T-20261019-ferr-criterios.md) | Feito | `1-Documentos/ferramentas/criterios.md` |
| [Levantar e comparar ferramentas de BI](../tasks/T-20261019-ferr-comparativo-bi.md) | Feito | `1-Documentos/ferramentas/comparativo-bi.md` |
| [Levantar e comparar canais de alerta](../tasks/T-20261019-ferr-comparativo-alerta.md) | Feito | `1-Documentos/ferramentas/comparativo-alerta.md` |
| [Levantar o ambiente de execucao do Airflow](../tasks/T-20261019-ferr-ambiente-airflow.md) | Feito | `1-Documentos/ferramentas/ambiente-airflow.md` |
| [ADR: escopo de orgaos da carga](../tasks/T-20261019-adr-escopo-orgaos.md) | Feito | `1-Documentos/adrs/0001-escopo-de-orgaos.md` |
| [ADR: ferramenta do painel](../tasks/T-20261019-adr-ferramenta-bi.md) | Feito | `1-Documentos/adrs/0002-ferramenta-do-painel.md` |
| [ADR: canal de alerta](../tasks/T-20261019-adr-canal-alerta.md) | Feito | `1-Documentos/adrs/0003-canal-de-alerta.md` |
| [ADR: nome do beneficiario na camada analitica](../tasks/T-20261019-adr-beneficiario-lgpd.md) | Feito | `1-Documentos/adrs/0004-beneficiario-na-analitica.md` |

## G4. Codigo novo (11)

| Tarefa | Status | Onde ficou |
|---|---|---|
| [Modulo de alerta (mensagem e envio)](../tasks/T-20261019-alerta-modulo.md) | Feito | `3-Etl/dags/scdp/alerta.py`, `tests/test_alerta.py` |
| [Ligar alerta na DAG diaria](../tasks/T-20261019-alerta-dag-diaria.md) | Feito | `3-Etl/dags/dag_carga_diaria.py`, `tests/test_cli_e_dags.py` |
| [Ligar alerta na DAG completa](../tasks/T-20261019-alerta-dag-completa.md) | Feito | `3-Etl/dags/dag_carga_completa.py`, `tests/test_cli_e_dags.py` |
| [Config: CODIGO_ORGAO aceita lista](../tasks/T-20261019-orgaos-config.md) | Feito | `3-Etl/dags/scdp/config.py`, `tests/test_orgaos_config.py` |
| [Pipeline: percorrer varios orgaos](../tasks/T-20261019-orgaos-pipeline.md) | Feito | `3-Etl/dags/scdp/pipeline.py`, `3-Etl/dags/scdp/cli.py`, `tests/test_orgaos_pipeline.py` |
| [Controle: ler a contagem anterior da janela](../tasks/T-20261019-janela-queda-leitura.md) | Feito | `3-Etl/dags/scdp/controle.py`, `tests/test_queda_leitura.py` |
| [Pipeline: avisar queda de contagem na janela](../tasks/T-20261019-janela-queda-aviso.md) | Feito | `3-Etl/dags/scdp/pipeline.py`, `tests/test_queda_aviso.py` |
| [Estender a dim_data ate 2035](../tasks/T-20261019-dim-data-2035.md) | Feito | `3-Etl/dags/sql/schema.sql`, `tests/test_dim_data.py` |
| [Script do gate de janelas](../tasks/T-20261019-validar-carga-script.md) | Feito | `2-Scripts/validar_carga_completa.py`, `tests/test_validar_carga.py` |
| [Ligar o gate de janelas na DAG completa](../tasks/T-20261019-validar-carga-dag.md) | Feito | `3-Etl/dags/dag_carga_completa.py`, `tests/test_validar_carga_dag.py` |
| [Fixar as actions do CI por SHA](../tasks/T-20261019-ci-actions-sha.md) | Feito | `.github/workflows/ci.yml`, `tests/test_ci_actions_fixadas.py` |

## G5. Painel (5)

| Tarefa | Status | Onde ficou |
|---|---|---|
| [View vw_kpi_mes](../tasks/T-20261019-views-kpi-mes.md) | Cancelada (o painel calcula os KPIs) | `3-Etl/dags/sql/schema.sql`, `tests/test_view_kpi_mes.py` |
| [View vw_kpi_orgao](../tasks/T-20261019-views-kpi-orgao.md) | Cancelada (o painel calcula os KPIs) | `3-Etl/dags/sql/schema.sql`, `tests/test_view_kpi_orgao.py` |
| [View vw_kpi_situacao](../tasks/T-20261019-views-kpi-situacao.md) | Cancelada (o painel calcula os KPIs) | `3-Etl/dags/sql/schema.sql`, `tests/test_view_kpi_situacao.py` |
| [Papel somente leitura para o painel](../tasks/T-20261019-papel-leitura-painel.md) | Feito | `3-Etl/dags/sql/papel_leitura.sql`, `tests/test_papel_leitura.py` |
| [Especificacao do painel](../tasks/T-20261019-painel-especificacao.md) | Cancelada (painel fora do escopo) | `4-DataViz/especificacao-painel.md`, `tests/test_especificacao_painel.py` |

## G6. Validacao e entrega (6)

| Tarefa | Status | Onde ficou |
|---|---|---|
| [Runbook: validar a carga completa desde 2025](../tasks/T-20261019-runbook-carga-real.md) | Feito | `1-Documentos/validacao/carga-completa-real.md` |
| [Runbook: exercitar registro tardio](../tasks/T-20261019-runbook-registro-tardio.md) | Feito | `1-Documentos/validacao/registro-tardio.md` |
| [Manual de operacao](../tasks/T-20261019-manual-operacao.md) | Feito | `1-Documentos/MANUAL.md` |
| [Manual de recuperacao de falhas](../tasks/T-20261019-manual-recuperacao.md) | Feito | `1-Documentos/MANUAL-recuperacao.md` |
| [Atualizar PRD e README com o estado real](../tasks/T-20261019-prd-atualizacao.md) | Feito | `1-Documentos/PRD.md`, `README.md` |
| [Checklist final de entrega](../tasks/T-20261019-checklist-entrega.md) | Feito | `1-Documentos/checklist-entrega.md` |

## G3. Testes da API reproduziveis (3)

| Tarefa | Status | Onde ficou |
|---|---|---|
| [Script reproduzivel que consulta uma janela e conta viagens](../tasks/T-20261019-api-contrato-base.md) | Feito | `2-Scripts/testar_janelas_api.py`, `tests/test_testar_janelas_api.py` |
| [Casos que devem dar certo: dentro do mes, mes+1, mes+12 e dia unico](../tasks/T-20261019-api-contrato-sucesso.md) | Feito | `2-Scripts/casos_janela_ok.json`, `tests/test_casos_janela_ok.py` |
| [Casos que devem dar 400 ou vazio](../tasks/T-20261019-api-contrato-erro.md) | Feito | `2-Scripts/casos_janela_erro.json`, `tests/test_casos_janela_erro.py` |
