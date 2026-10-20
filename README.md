# Painel SCDP Viagens

Carga incremental das viagens a serviço do Governo Federal (SCDP), obtidas na API do Portal da Transparência, para o PostgreSQL, em modelo medalhão (staging, intermediária e analítica), com controle da carga por janela de datas. A base alimenta um painel de viagens.

Estado em 19/10/2026: carga testada com o órgão `33000` (MPS). Varredura de 2026 com 1.460 viagens, repetida com resultado idêntico. Carga completa desde 2025 e DAGs do Airflow ainda não executadas. Detalhes e decisões em `1-Documentos/PRD.md`.

## Estrutura do projeto
| Pasta | Conteúdo |
|---|---|
| `1-Documentos/` | `PRD.md`, `referencia_api.md` (spec dos 109 endpoints), `dicionario-de-dados-viagens.md`, `perguntas-dono-da-api.md` (com os testes feitos) e `referencia/` (códigos de órgãos SIAFI e SIAPE) |
| `2-Scripts/` | Exploração e validação: `consulta_viagens.py`, `varredura_2026.py` e `postman/`. `saidas/` guarda dados gerados (não versionado) |
| `3-Etl/dags/` | DAGs do Airflow, `carga_viagens.py` (ponto de entrada), o pacote `scdp/` (código da carga) e `sql/schema.sql` (DDL) |
| `tests/` | Testes unitários e de integração (rodam no CI com PostgreSQL) |
| `4-DataViz/` | Painel |
| `5-Images/` | Imagens e prints |

## Como rodar
1. `copy .env.example .env` e preencher a chave da API e os dados do banco. **O `.env` não vai para o git.**
2. Carga diária: `python -I 3-Etl/dags/carga_viagens.py --modo diario`
3. Carga completa: `python -I 3-Etl/dags/carga_viagens.py --modo completo --desde 2025-01`
4. Refazer intermediária e analítica sem chamar a API: `python -I 3-Etl/dags/carga_viagens.py --reconstruir-silver`
5. Só contar na API, sem banco: `python -I 3-Etl/dags/carga_viagens.py --dry-run --desde 2026-08`

Requisitos: Python 3 com `requests` e `psycopg2`. Sugestão de agendamento: diário às 02:00 e completo a cada 10 dias às 03:30 (faixa de 700 requisições por minuto). O código sai com código 1 se sobrar janela com erro ou pendente.

Variáveis do `.env` (modelo em `.env.example`): `PORTAL_TRANSPARENCIA_API_KEY`, `PORTAL_TRANSPARENCIA_BASE_URL`, `CODIGO_ORGAO`, `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGSSLMODE`, `DATABASE_URL` (opcional, tem prioridade) e `SCHEMA_STG`, `SCHEMA_INT`, `SCHEMA_ANA`. Variáveis de ambiente (como as do Airflow) têm prioridade sobre o arquivo.

## Arquitetura do código (extração, carga e transformação)
O código fica no pacote `3-Etl/dags/scdp/`, separado por responsabilidade. A configuração é um objeto único (`Config`), as dependências são injetadas (o pipeline recebe o cliente da API e o controle, o que permite testar sem rede) e as mensagens saem por `logging`.

| Módulo | Etapa | Responsabilidade |
|---|---|---|
| `extracao.py` | Extração (E) | Único ponto de contato com a API: paginação, tentativas, `Retry-After` e pausa pelo limite do horário de Brasília |
| `carga.py` | Carga (L) | Conexão com o PostgreSQL, schemas configuráveis e gravação do JSON como veio na staging (`stg_viagem`) |
| `transformacao.py` | Transformação (T) | Detecção do que é novo ou alterado (hash), staging → intermediária e intermediária → analítica, tudo incremental |
| `controle.py` | Observabilidade | Janelas, erros abertos e resolvidos, execuções (schema `staging`) |
| `janelas.py` | Planejamento | Combinações de mês de ida × mês de retorno, quais janelas ler em cada modo e ordem de retomada |
| `pipeline.py` | Orquestração | Executa janela a janela: extrai, carrega, transforma, concilia, registra erros e retoma |
| `config.py` / `cli.py` | Entrada | Variáveis de ambiente e linha de comando |

`carga_viagens.py` só chama `scdp.cli.main`; as DAGs do Airflow executam esse arquivo.

## Modelo de dados (medalhão)
| Camada | Schema e prefixo | Conteúdo |
|---|---|---|
| Staging (bronze) | `staging`, `stg_` | `stg_viagem`: o JSON de cada viagem como a API devolveu, mais janela de origem, hash e datas de carga. Sem regra de negócio |
| Intermediária (silver) | `intermediaria`, `int_` | `int_viagem`: colunas tipadas e derivadas (`dias_afastamento`, `valor_outros_gastos`) |
| Analítica (gold) | `analitica`, `fct_`, `dim_`, `obt_` | `fct_viagem`, `dim_data`, `dim_orgao`, `dim_ug`, `dim_beneficiario`, `dim_perfil_viagem` e `obt_viagem` (one big table) |
| Controle | `staging`, `ctl_` | `ctl_janela` (uma linha por janela), `ctl_execucao`, `ctl_camada` (marca d'água da analítica), views `vw_ctl_pendencias` e `vw_ctl_tardios` |

**Todas as cargas são incrementais.** A staging só grava o que é novo ou mudou (comparação por hash). A intermediária atualiza só essas viagens. A analítica processa só o que mudou desde a última marca d'água, e uma mudança de nome de órgão ou UG atualiza as linhas afetadas da `obt_viagem`.

## Como as datas são combinadas (para não perder viagens)
A API filtra **ida** e **retorno** por duas janelas independentes, cada uma com no máximo 1 mês. A viagem só aparece se cair nas duas, então uma consulta única perde as viagens longas. A carga varre todas as combinações de mês de ida × mês de retorno, sempre com mês de calendário:

| Tipo | Combinação | Exemplo (março/2026) |
|---|---|---|
| Dentro do mês | ida M, retorno M | 312 viagens |
| Cruza a virada do mês | ida M, retorno M+1 | 18 viagens |
| Longa | ida M, retorno de M+2 até M+12 | 3 viagens |
| Anomalias (retorno antes da ida, retorno em 2028) | não consultadas | nada encontrado |

Desde 2025-01 são 312 janelas (24 meses de ida, incluindo 2 meses futuros, × 13 distâncias), cada uma paginada até a resposta `[]`.
Em 2026: das 1.460 viagens, 1.323 começam e terminam no mesmo mês, 125 retornam no mês seguinte e 12 terminam de 2 a 6 meses depois. A mais longa teve 181 dias.

- **Modo diário:** relê as janelas com ida ou retorno nos últimos 3 meses, mais as pendentes ou com erro (156 das 312).
- **Modo completo:** relê todas as janelas; pega registros antigos que entraram com atraso (marcados como `TARDIO`).

## Controle, erros e retomada (schema `staging`)
Cada janela só vira `OK` se a quantidade devolvida pela API for igual à carregada. Janela que devolve menos registros do que na leitura anterior é relida e gera aviso.

**Erros:** toda falha é gravada em `staging.ctl_erro` (uma linha por janela e etapa: `api`, `banco`, `conciliacao`, `analitica` ou `execucao`), com código, mensagem, número de tentativas e primeira e última ocorrência. Quando o erro é corrigido, a linha **sai de `ctl_erro`** e vai para `ctl_erro_historico`, com a data e a execução que resolveu.

**Tentativas:** dentro de cada chamada são até 8 tentativas com espera crescente (5xx, 504, queda de rede) e espera do `Retry-After` em 429. Janelas que ainda falharam ganham mais 2 rodadas no fim da execução. Erro 400 é registrado e a carga continua; erro 401 (chave inválida) aborta a execução, porque todas falhariam.

**Retomada:** a execução seguinte começa pelas janelas com erro, interrompidas ou pendentes e depois segue em ordem. Uma execução que caiu sem registrar o fim (mais de 12 horas) é marcada `INTERROMPIDA` e gera um erro da etapa `execucao`, resolvido na próxima execução limpa. Uma falha na analítica não perde dados: a marca d'água só avança quando a carga termina, então ela é refeita sozinha.

**Consultas de monitoramento:** `vw_ctl_saude` (uma linha com o resumo: janelas pendentes, erros abertos e resolvidos, última execução, marca da analítica), `vw_ctl_erros_abertos` (com horas em aberto), `vw_ctl_execucoes` (status e duração), `vw_ctl_pendencias` e `vw_ctl_tardios`. O código de saída é 0 (limpa), 1 (erro aberto, janela pendente ou execução abortada) ou 3 (outra execução da carga em andamento para o mesmo órgão).

**Segurança e robustez:** uma trava no banco (`pg_try_advisory_lock`) permite uma execução por vez por órgão, o que também protege a marca d'água da analítica; os nomes de schema são validados; chave da API e senhas são trocadas por `***` antes de irem para logs e para `ctl_erro`; resposta 200 que não é JSON é tentada de novo; 403 aborta como o 401; texto vazio, inválido ou fora do limite vira `NULL` na intermediária (o JSON original fica intacto na staging); ids repetidos pela API na mesma janela são descartados com aviso.

## Regras da API (resumo)
- Base: `https://api.portaldatransparencia.gov.br/api-de-dados`; autenticação pelo header `chave-api-dados`.
- `GET /viagens` exige `dataIdaDe`, `dataIdaAte`, `dataRetornoDe`, `dataRetornoAte` (`dd/MM/yyyy`), `codigoOrgao` (SIAFI) e `pagina`. Cada par de datas ≤ 1 mês, senão 400. 15 registros por página.
- Limites oficiais: 400 requisições por minuto das 6:00 às 23:59 e 700 das 0:00 às 5:59. O script usa 50%.
- `codigoOrgao` filtra a entidade, não o ministério. No MPS: `33000` (142 viagens em ago/2026), INSS `37202` (1.265) e PREVIC `33206` (22).
- Só existem 3 endpoints de viagens. Passagens, trechos e pagamentos existem apenas no download em lote do portal.
- CPF vem mascarado. Em viagens sigilosas o nome vem como "Informações protegidas por sigilo".
- `valorTotalViagem` = passagem + diárias + taxa + restituição + outros gastos (este último não existe na API; explica 26 de 1.460 totais que não fecham).
- Dados atualizados com atraso: a tela do portal informou "dados atualizados até 04/09/2026" em 19/10/2026.

## Decisões e pendências
- **CPF:** permanece mascarado como a API entrega, em todas as camadas.
- **`motivo` (texto livre):** fora da analítica; fica na intermediária e no JSON da staging.
- **Nome do beneficiário:** segue na analítica; confirmar se permanece.
- **Escopo de órgãos:** só `33000` ou o MPS inteiro (INSS, PREVIC)? Define o volume da carga.
- **Código `308819`:** não existe como órgão no SIAFI nem no SIAPE; origem a esclarecer.
- **Download em lote:** avaliar para o histórico, passagens, trechos e pagamentos.
- **Airflow:** as DAGs existem em `3-Etl/dags/`, mas há `dag_id` duplicado entre os arquivos e o agendamento ainda precisa de ajuste de fuso e de intervalo (ver avaliação das DAGs).
- **Perguntas para o dono da API:** `1-Documentos/perguntas-dono-da-api.md`.

## Limites conhecidos
- Viagens sem data de retorno não entram em nenhuma janela de consulta.
- Retorno mais de 12 meses depois da ida não é consultado (nenhum caso observado).
- Registro antigo que entra tarde é percebido, no pior caso, na próxima execução do modo completo (até 10 dias).
- Viagens removidas da API não são apagadas das tabelas.
