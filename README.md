# Painel SCDP Viagens

Carga incremental das viagens a serviço do Governo Federal (SCDP), obtidas na API do Portal da Transparência, para o PostgreSQL, em modelo medalhão (staging, intermediária e analítica), com controle da carga por janela de datas. A base alimenta um painel de viagens.

Estado em 19/10/2026: carga testada com o órgão `33000` (MPS). Varredura de 2026 com 1.460 viagens, repetida com resultado idêntico. Carga completa desde 2025 e DAGs do Airflow ainda não executadas. Detalhes e decisões em `1-Documentos/PRD.md`.

## Estrutura do projeto
| Pasta | Conteúdo |
|---|---|
| `1-Documentos/` | `PRD.md`, `referencia_api.md` (spec dos 109 endpoints), `dicionario-de-dados-viagens.md`, `contrato-dados-viagens.md` (formato do download e conciliação com a API, 2025 e 2026), `perguntas-dono-da-api.md` (com os testes feitos) e `referencia/` (códigos de órgãos SIAFI e SIAPE) |
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

Requisitos: Python 3 com `requests` e `psycopg2`. Sugestão de agendamento: diário às 02:00 e completo às 03:30 dos dias 1, 11 e 21 (a cada ~10 dias), no horário de Brasília (faixa de 700 requisições por minuto). Os schemas `staging`, `intermediaria` e `analitica` precisam existir antes da primeira carga (`CREATE SCHEMA`). O código de saída é 0 (limpa), 1 (erro aberto, pendência ou execução abortada), 2 (erro de configuração ou de linha de comando), 3 (outra execução em andamento) ou 143 (interrompida por `SIGTERM`).

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
| `config.py` / `cli.py` | Entrada | Variáveis de ambiente (com validação e mascaramento de segredos) e linha de comando |
| `erros.py` / `codigos.py` / `dag_util.py` | Apoio | Descrição segura de exceções (sem segredos nem valores pessoais), códigos de saída e montagem do comando das DAGs |

`carga_viagens.py` só chama `scdp.cli.main`; as DAGs do Airflow executam esse arquivo.

## Modelo de dados (medalhão)
| Camada | Schema e prefixo | Conteúdo |
|---|---|---|
| Staging (bronze) | `staging`, `stg_` | `stg_viagem`: o JSON de cada viagem como a API devolveu, mais janela de origem, hash e datas de carga. Sem regra de negócio |
| Intermediária (silver) | `intermediaria`, `int_` | `int_viagem`: colunas tipadas e derivadas (`dias_afastamento`, `valor_outros_gastos`) |
| Analítica (gold) | `analitica`, `fct_`, `dim_`, `obt_` | `fct_viagem`, `dim_data`, `dim_orgao`, `dim_ug`, `dim_beneficiario`, `dim_perfil_viagem` e `obt_viagem` (one big table) |
| Controle | `staging`, `ctl_` | `ctl_janela` (uma linha por janela), `ctl_execucao`, `ctl_erro` (erros abertos), `ctl_erro_historico` (resolvidos), `ctl_camada` (marca d'água da analítica), `ctl_schema` (versão do DDL), views `vw_ctl_*` |

**Todas as cargas são incrementais.** A staging só grava o que é novo ou mudou (comparação por hash). A intermediária atualiza só essas viagens. A analítica processa só o que mudou desde a última marca d'água, e uma mudança de nome de órgão ou UG atualiza as linhas afetadas da `obt_viagem`.

## Como as datas são combinadas (para não perder viagens)
A API filtra **ida** e **retorno** por duas janelas independentes, cada uma com no máximo 1 mês. A viagem só aparece se cair nas duas, então uma consulta única perde as viagens longas. A carga varre todas as combinações de mês de ida × mês de retorno, sempre com mês de calendário:

| Tipo | Combinação | Exemplo (março/2026) |
|---|---|---|
| Dentro do mês | ida M, retorno M | 312 viagens |
| Cruza a virada do mês | ida M, retorno M+1 | 18 viagens |
| Longa | ida M, retorno de M+2 até M+12 | 3 viagens |
| Anomalias (retorno antes da ida, retorno em 2028) | não consultadas | nada encontrado |

Diagrama do processo: `1-Documentos/diagrama-busca-por-datas.excalidraw` (abre em excalidraw.com), com prévia em `5-Images/diagrama-busca-por-datas.png`.

Desde 2025-01 são 312 janelas (24 meses de ida, incluindo 2 meses futuros, × 13 distâncias), cada uma paginada até a resposta `[]`.
Em 2026: das 1.460 viagens, 1.323 começam e terminam no mesmo mês, 125 retornam no mês seguinte e 12 terminam de 2 a 6 meses depois. A mais longa teve 181 dias.

- **Modo diário:** relê as janelas com ida ou retorno nos últimos 3 meses, mais as pendentes ou com erro (156 das 312).
- **Modo completo:** relê todas as janelas; pega registros antigos que entraram com atraso (o log marca `TARDIO` na janela; a view `vw_ctl_tardios` usa outro critério: viagens antigas carregadas nos últimos 2 dias).

## Controle, erros e retomada (schema `staging`)
Cada janela só vira `OK` se a quantidade devolvida pela API for igual à carregada. Janela que devolve menos registros do que na leitura anterior é relida e gera aviso.

**Erros:** toda falha é gravada em `staging.ctl_erro` (uma linha por janela e etapa: `api`, `banco` ou `conciliacao`; as etapas `analitica` e `execucao` não têm janela), com código, mensagem, número de tentativas e primeira e última ocorrência. Quando o erro é corrigido, a linha **sai de `ctl_erro`** e vai para `ctl_erro_historico`, com a data e a execução que resolveu.

**Tentativas:** dentro de cada chamada são até 8 tentativas com espera crescente (5xx, 504, queda de rede) e espera do `Retry-After` em 429. Janelas que ainda falharam ganham mais 2 rodadas no fim da execução. Erro 400 e 404 são registrados, a carga continua e a janela não é repetida nas rodadas extras (o erro é permanente); 401 e 403 (chave inválida ou bloqueada) abortam a execução, porque todas as janelas falhariam.

**Retomada:** a execução seguinte começa pelas janelas com erro, interrompidas ou pendentes e depois segue em ordem. Como só uma execução roda por vez, quem pega a trava e encontra uma execução sem fim sabe que ela morreu: marca como `INTERROMPIDA` na hora e gera um erro da etapa `execucao`, resolvido na próxima execução limpa. Um `SIGTERM` (por exemplo, o timeout do Airflow) também marca a execução atual como `INTERROMPIDA` antes de sair. Uma falha na analítica não perde dados: a marca d'água só avança quando a carga termina, então ela é refeita sozinha.

**Consultas de monitoramento:** `vw_ctl_saude` (uma linha com o resumo: janelas pendentes, erros abertos e resolvidos, última execução, marca da analítica), `vw_ctl_erros_abertos` (com horas em aberto), `vw_ctl_execucoes` (status e duração), `vw_ctl_pendencias` e `vw_ctl_tardios`. O código de saída é 0 (limpa), 1 (erro aberto, janela pendente ou execução abortada) 2 (erro de configuração ou de linha de comando) ou 3 (outra execução em andamento). Nas DAGs, o código 3 vira tarefa *skipped* (`skip_on_exit_code`).

**Segurança e robustez:** uma trava no banco (`pg_try_advisory_lock`, uma por combinação dos três schemas) permite uma execução por vez, o que protege a marca d'água da analítica e as tabelas de controle; o DDL só é reaplicado quando o `schema.sql` ou os nomes dos schemas mudam (hash do texto resolvido em `ctl_schema`), já com a trava em mãos; os nomes de schema são validados e a URL da API precisa ser `https://`; chave da API e senhas (inclusive as da `DATABASE_URL`) são trocadas por `***` antes de irem para logs e para `ctl_erro`, e as mensagens de erro do PostgreSQL entram sem o `DETAIL` nem o valor ofensivo (que podem trazer nome e CPF parcial); a API não é seguida em redirecionamentos (a chave iria junto); a paginação para se a API devolver a mesma página, algo que não é lista, ou mais de 1.000 páginas; resposta 200 que não é JSON é tentada de novo; `Retry-After` inválido usa 60 s, com teto de 300 s; texto vazio, inválido ou fora do limite vira `NULL` na intermediária (o JSON original fica intacto na staging) e a janela ganha um aviso com a quantidade; valores com mais de duas casas são arredondados de forma explícita; ids repetidos pela API na mesma janela são descartados com aviso; a conexão usa *keepalive*, mas a trava é de sessão: ela exige conexão direta (não funciona atrás de pooler em modo transaction) e, se o host do worker cair sem fechar a conexão, o servidor só a solta quando perceber a sessão morta (por isso as execuções seguintes saem com código 3 até lá).

## Regras da API (resumo)
- Base: `https://api.portaldatransparencia.gov.br/api-de-dados`; autenticação pelo header `chave-api-dados`.
- `GET /viagens` exige `dataIdaDe`, `dataIdaAte`, `dataRetornoDe`, `dataRetornoAte` (`dd/MM/yyyy`), `codigoOrgao` (SIAFI) e `pagina`. Cada par de datas ≤ 1 mês, senão 400. 15 registros por página.
- Limites oficiais: 400 requisições por minuto das 6:00 às 23:59 e 700 das 0:00 às 5:59. O script usa 50%.
- `codigoOrgao` filtra a entidade, não o ministério. No MPS: `33000` (142 viagens em ago/2026), INSS `37202` (1.265) e PREVIC `33206` (22).
- Só existem 3 endpoints de viagens. Passagens, trechos e pagamentos existem apenas no download em lote do portal.
- CPF vem mascarado. Em viagens sigilosas o nome vem como "Informações protegidas por sigilo".
- `valorTotalViagem` = passagem + diárias + taxa + restituição + outros gastos (este último não existe na API; explica 26 de 1.460 totais que não fecham).
- Dados atualizados com atraso: a tela do portal informou "dados atualizados até 04/09/2026" em 19/10/2026.

## Links oficiais
| Para quê | Link |
|---|---|
| **Download em lote das viagens (um ZIP por ano, 2011 a 2027)** | https://portaldatransparencia.gov.br/download-de-dados/viagens (ex.: `.../viagens/2025` redireciona para `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/viagens/2025_AAAAMMDD_Viagens.zip`) |
| Dicionário de dados das viagens | https://portaldatransparencia.gov.br/dicionario-de-dados/viagens |
| API: documentação interativa (Swagger) | https://api.portaldatransparencia.gov.br/swagger-ui/index.html |
| API: especificação OpenAPI | https://api.portaldatransparencia.gov.br/v3/api-docs |
| API: página oficial (limites de requisição e termos de uso) | https://portaldatransparencia.gov.br/api-de-dados |
| API: cadastro da chave | https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email |
| Consulta de viagens na tela (para conferir os dados) | https://portaldatransparencia.gov.br/viagens/consulta |

O download automatizado com `curl` precisa de um `User-Agent` de navegador. Formato dos arquivos e conciliação com a API: `1-Documentos/contrato-dados-viagens.md`.

## Decisões e pendências
- **CPF:** permanece mascarado como a API entrega, em todas as camadas.
- **`motivo` (texto livre):** fora da analítica; fica na intermediária e no JSON da staging.
- **Nome do beneficiário:** segue na analítica; confirmar se permanece.
- **Escopo de órgãos:** só `33000` ou o MPS inteiro (INSS, PREVIC)? Define o volume da carga.
- **Código `308819`:** não existe como órgão no SIAFI nem no SIAPE; origem a esclarecer.
- **Download em lote:** avaliar para o histórico, passagens, trechos e pagamentos.
- **Airflow:** duas DAGs em `3-Etl/dags/` (`scdp_carga_diaria` às 02:00 e `scdp_carga_completa` às 03:30 dos dias 1, 11 e 21, ambas em `America/Sao_Paulo`). A diária é pulada se a trava estiver ocupada; a completa falha e é repetida. A chave da API e a senha do banco chegam pelo ambiente do worker (Connections/Variables ainda não usadas).
- **Perguntas para o dono da API:** `1-Documentos/perguntas-dono-da-api.md`.

## Limites conhecidos
- Viagens sem data de retorno não entram em nenhuma janela de consulta.
- Retorno mais de 12 meses depois da ida não é consultado (nenhum caso observado).
- Registro antigo que entra tarde é percebido, no pior caso, na próxima execução do modo completo (até 10 dias).
- Viagens removidas da API não são apagadas das tabelas.
