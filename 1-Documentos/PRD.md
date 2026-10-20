# PRD: Painel SCDP Viagens

Versão 0.1, 19/10/2026. Estado: rascunho para validação.

## 1. Contexto e problema
Os dados de viagens a serviço do Governo Federal (SCDP) são publicados no Portal da Transparência. Não há uma base local, histórica e conciliada para análise. A API do portal é limitada (filtros obrigatórios, janela máxima de 1 mês por par de datas, 15 registros por página, publicação com atraso), então uma carga ingênua perde registros e não percebe correções tardias.

## 2. Objetivo
Manter uma tabela de staging no banco com **todas** as viagens do(s) órgão(s) definido(s), de 01/01/2025 em diante, atualizada automaticamente, com controle que prove o que foi e o que não foi carregado, e base para um painel de viagens.

### Métricas de sucesso
- 100% das janelas planejadas com status `OK` e `qtd_api = qtd_carregada`.
- Viagens que entram com atraso são detectadas e sinalizadas (campo `TARDIO`) em até 1 execução diária.
- Duas varreduras completas seguidas devolvem os mesmos ids (já validado em 19/10/2026: 1.460 viagens, 0 diferenças).
- Nenhuma suspensão de token por excesso de requisições.

## 3. Escopo
**Dentro:** extração via API `/viagens`, staging, tabelas de controle, execução diária e completa, documentação da API, validação de integridade.
**Fora (nesta versão):** o painel em si (BI), enriquecimento com dados de servidores, CPF completo, dados de passagens/trechos/pagamentos (ver decisões em aberto, seção 10).

## 4. Usuários
- Analistas que consomem a staging/painel.
- Engenharia de dados que opera a carga (Python hoje; Pentaho como alternativa avaliada).

## 5. Decisões de escopo em aberto (bloqueiam a carga final)
1. **Órgãos:** `codigoOrgao` filtra pela entidade, não pelo ministério. No MPS, em ago/2026: `33000` = 142 viagens, INSS `37202` = 1.265, PREVIC `33206` = 22. Definir se o escopo é só `33000` ou o MPS inteiro.
2. **Código `308819`:** informado como órgão, mas não existe nas listas SIAFI (766 órgãos) nem SIAPE (641). Origem a confirmar. Nada nos dados carregados o contém.
3. **API × download em lote:** o portal recomenda as planilhas de dados abertos para o conjunto completo (um download por ano, 2011–2027, 4 arquivos: Viagem, Passagem, Pagamento, Trecho). Os arquivos de passagem, trecho e pagamento não existem na API. Formato, tamanho e encoding ainda não foram verificados.

## 6. Requisitos funcionais
| ID | Requisito | Estado |
|---|---|---|
| RF1 | Consultar `/viagens` para cada combinação mês de ida × mês de retorno (até 12 meses depois), com janelas de 1 mês | Implementado, testado na API |
| RF2 | Paginar até resposta `[]` (15 por página) | Implementado |
| RF3 | Gravar na bronze o JSON como recebido, com upsert por `id`; novo = insere, alterado = atualiza (hash do registro), igual = ignora; propagar para a silver | Implementado e testado em banco (ago–set/2026) |
| RF4 | Tabela de controle por janela: status, qtd_api, qtd_carregada, qtd_novos, qtd_alterados, tentativas, aviso, erro | Implementado e testado em banco |
| RF5 | Fechar janela como `OK` só se `qtd_api = qtd_carregada` | Implementado e testado em banco |
| RF6 | Modo diário: janelas com ida ou retorno nos últimos 3 meses, mais pendentes ou com erro | Implementado |
| RF7 | Modo completo (dias 1, 11 e 21, a cada ~10 dias): todas as janelas desde 2025-01 | Implementado |
| RF8 | Detectar e sinalizar viagens antigas que entraram tarde (`TARDIO`, view `vw_ctl_tardios`) | Implementado; cenário de atraso real ainda não exercitado |
| RF9 | Planejar também os 2 meses futuros, para pegar viagens agendadas | Implementado |
| RF10 | Retomar de onde parou após falha | Implementado por controle de janela |
| RF11 | Aceitar lista de órgãos (hoje um só, via `CODIGO_ORGAO`) | **Pendente**, depende da decisão 5.1 |
| RF12 | Alerta quando houver erro/pendência (código de saída 1; 2 = configuração; 3 = outra execução em andamento) | Implementado como código de saída; alerta a definir |
| RF13 | Gravar erros em `staging.ctl_erro` (janela, etapa, código, mensagem, tentativas, datas) e removê-los da tabela quando corrigidos, preservando-os em `ctl_erro_historico` | Implementado; testado na base real (ciclo 401 → correção) |
| RF14 | Tentativas: até 8 por chamada com espera crescente, `Retry-After` em 429, 2 rodadas extras no fim; 400 e 404 não derrubam a carga nem são repetidos nas rodadas extras; 401 e 403 abortam | Implementado |
| RF15 | Retomar de onde parou: janelas com erro, interrompidas ou pendentes primeiro; execução sem fim vira `INTERROMPIDA` | Implementado |
| RF16 | Observabilidade no schema `staging`: `vw_ctl_saude`, `vw_ctl_erros_abertos`, `vw_ctl_execucoes`, `vw_ctl_pendencias` | Implementado |

## 7. Requisitos não funcionais
- **Rate limit (oficial):** 400 req/min das 6:00 às 23:59; 700 req/min das 0:00 às 5:59. O script usa 50% do limite e respeita `Retry-After` em 429. Acima do limite o token pode ser suspenso.
- **Resiliência:** retry com backoff em 5xx e erros de rede (504 é frequente); erro 400/404 registra a janela e a carga segue; 401/403 abortam a execução.
- **Segurança:** a chave fica no `.env`, que não deve ser versionado. CPF só existe mascarado na API (`***.584.117-**`); viagens sigilosas vêm sem nome.
- **Execução recomendada:** diário às 02:00 e completo às 03:30 dos dias 1, 11 e 21 (a cada ~10 dias), no horário de Brasília (faixa de 700 req/min). As DAGs fixam `America/Sao_Paulo` porque a interface do Airflow mostra UTC.
- **Desempenho esperado:** completo ≈ 400 requisições (cerca de 2 a 3 minutos com o limite noturno), para um órgão.

## 8. Fonte de dados e regras da API (resumo)
Detalhes em `CLAUDE.md` e `1-Documentos/referencia_api.md` (spec completa, 109 endpoints).
- Endpoints de viagens: `/viagens` (período + órgão), `/viagens/{id}` (mesmo objeto, conferido), `/viagens-por-cpf` (exige CPF completo, não testado).
- Os 6 parâmetros de `/viagens` são obrigatórios; cada par de datas ≤ 1 mês (`De` = `Ate` aceito, inclusivo).
- Viagens longas só aparecem combinando mês de ida com mês de retorno; a mais longa em 2026 teve 181 dias. Retorno antes da ida, ou 7+ meses depois, não retornou nada.
- Campos: id, PCDP, motivo, situação, tipo, urgência, beneficiário, cargo/função, órgão e órgão de pagamento, UG, datas, valores (total, passagem, diárias, taxa de agenciamento, restituição, devolução, multa).
- `valorTotalViagem` = passagem + diárias + taxa + restituição + **outros gastos** (esse campo existe no dicionário oficial mas não na API).
- Atraso de publicação: o portal informa "dados atualizados até 04/09/2026" (consulta em 19/10/2026).
- Viagens sem data de retorno (em andamento) não são alcançáveis, pois as 4 datas são obrigatórias.

### 8.0 Como as datas foram combinadas para não perder viagens
A API filtra a **ida** e o **retorno** por janelas independentes, cada uma com no máximo 1 mês, e a viagem só aparece se cair nas duas. Uma consulta única não cobre viagens longas, então o plano é varrer todas as combinações (mês de ida × mês de retorno), sempre com janelas de calendário (dia 1 ao último dia do mês):

| Tipo de viagem | Combinação consultada | Exemplo (março/2026) |
|---|---|---|
| Dentro do mês | ida no mês M, retorno no mesmo mês M | ida 01–31/03, retorno 01–31/03: 312 viagens |
| Cruza a virada do mês | ida em M, retorno em M+1 | ida 01–31/03, retorno 01–30/04: 18 viagens |
| Longa | ida em M, retorno em M+2 até M+12 | ida 01–31/03, retorno 01–30/06: 3 viagens |
| Anomalias | retorno antes da ida, ou retorno em 2028 | não devolveram nada |

Para cada mês de ida de 2026 (jan a dez) o script consulta o retorno do mesmo mês até 12 meses depois: 12 × 13 = 156 consultas por ano, cada uma paginada até `[]`. Só 26 combinações trouxeram dados. Agrupando as 1.460 viagens pela distância entre o mês de ida e o de retorno:

| Meses entre ida e retorno | Viagens |
|---|---|
| 0 (mesmo mês) | 1.323 |
| 1 | 125 |
| 2 | 5 |
| 3 | 4 |
| 4 | 0 |
| 5 | 2 |
| 6 | 1 |
| 7 a 12 | 0 |

A varredura foi repetida e devolveu exatamente os mesmos ids. Também funcionam janelas menores que 1 mês (uma semana, um dia), mas o padrão adotado é o mês inteiro. Detalhe do teste em `perguntas-dono-da-api.md` (seção 10).
Limite conhecido: viagens sem data de retorno não se encaixam em nenhuma janela de retorno.

**O que o script de carga (`3-Etl/dags/carga_viagens.py`) cobre** (conferido executando o planejamento dele):
| Tipo | Coberto? | Observação |
|---|---|---|
| Dentro do mês | Sim | distância 0 |
| Cruza a virada do mês | Sim | distância 1 |
| Longa (M+2 a M+12) | Sim | distâncias 2 a 12 |
| Anomalias (retorno antes da ida, retorno em 2028) | Não, de propósito | testadas e sem retorno de dados |

- **Planejamento desde 2025-01:** 312 janelas = 24 meses de ida (jan/2025 a dez/2026, incluindo 2 meses futuros) × 13 distâncias (0 a 12), 24 janelas por distância; cada janela é paginada até `[]`.
- **Modo diário:** relê 156 das 312 janelas, as com ida ou retorno nos últimos 3 meses, mais as pendentes ou com erro. Uma viagem antiga que termina agora entra; uma janela antiga inteira (ida e retorno em fevereiro, por exemplo) só é relida no modo completo.
- **Modo completo (a cada 10 dias):** relê as 312 janelas e pega registros antigos que entraram com atraso (`TARDIO`). No pior caso, um atraso desse tipo é percebido 10 dias depois.
- **Não cobertos:** retorno mais de 12 meses depois da ida (nenhum caso observado) e viagens sem data de retorno.

### 8.1 Endpoints da API usados ou avaliados
Base: `https://api.portaldatransparencia.gov.br/api-de-dados`. Autenticação: header `chave-api-dados`. Todos são GET.

| Endpoint | Parâmetros (obrigatórios em negrito) | Retorno | Uso no projeto |
|---|---|---|---|
| `/viagens` | **dataIdaDe, dataIdaAte, dataRetornoDe, dataRetornoAte** (dd/MM/yyyy), **codigoOrgao** (SIAFI), **pagina** | Lista de viagens (15 por página) | Fonte principal da carga |
| `/viagens/{id}` | **id** | Uma viagem (mesmo objeto da lista) | Conferência pontual |
| `/viagens-por-cpf` | **cpf** (completo), **pagina** | Lista de viagens | Não usado: CPF só vem mascarado |
| `/orgaos-siafi` | descricao, **pagina** | Lista (codigo, descricao); 766 órgãos | Descobrir `codigoOrgao` de `/viagens`. A busca diferencia maiúsculas e acentos |
| `/orgaos-siape` | descricao, **pagina** | Lista (codigo, descricao); 641 órgãos | Descobrir o código SIAPE usado em `/servidores` |
| `/servidores` | cpf, nome, orgaoServidorExercicio, orgaoServidorLotacao, tipoServidor, situacaoServidor, codigoFuncaoCargo, **pagina** (mínimo: órgão ou CPF) | Cadastro do servidor (CPF mascarado) | Opcional: ligar viagem ↔ servidor por nome + CPF parcial |
| `/servidores/{id}` | **id** | Cadastro do servidor | Opcional |
| `/servidores/remuneracao` | cpf ou id, **mesAno** (AAAAMM), **pagina** | Remuneração | Fora de escopo |
| `/pessoa-fisica` | cpf ou nis | Pessoa física | Não usado: exige CPF completo |

O portal tem 109 endpoints em 17 grupos (benefícios, despesas, contratos, licitações, convênios, sanções e outros). A lista completa, com parâmetros e campos de resposta, está em `1-Documentos/referencia_api.md`. Para viagens existem apenas os 3 primeiros endpoints. Não há endpoint de passagens, trechos ou pagamentos.

Respostas: 200 OK, 400 (parâmetro ausente, formato inválido ou janela maior que 1 mês), 401 (chave ausente ou inválida), 429 (limite excedido), 500, e 504 intermitente.

### 8.2 Links oficiais
| Para quê | URL |
|---|---|
| Documentação interativa (Swagger) | `https://api.portaldatransparencia.gov.br/swagger-ui/index.html` |
| Especificação OpenAPI (JSON) | `https://api.portaldatransparencia.gov.br/v3/api-docs` |
| Changelog da API | `https://api.portaldatransparencia.gov.br/changelog` |
| Página oficial da API (limites, regras, termos de uso) | `https://portaldatransparencia.gov.br/api-de-dados` |
| Cadastro da chave (token por e-mail) | `https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email` |
| Exemplos de uso (JavaScript, Java, PHP, .NET) | `https://portaldatransparencia.gov.br/pagina-interna/603579-api-de-dados-exemplos-de-uso` |
| Dicionário de dados de viagens | `https://portaldatransparencia.gov.br/dicionario-de-dados/viagens` |
| Download em lote de viagens (por ano) | `https://portaldatransparencia.gov.br/download-de-dados/viagens` |
| Consulta de viagens na tela (para conferir a API) | `https://portaldatransparencia.gov.br/viagens/consulta` |
| Descrição das viagens a serviço | `https://portaldatransparencia.gov.br/pagina-interna/603235-viagens` |

Observação: o portal bloqueia leitura automática (HTTP 405) das páginas fora da API, então elas só abrem em navegador.

## 9. Arquitetura e dados (modelo medalhão)
Extração (Python) → PostgreSQL, schema `staging` → painel. Pentaho é opcional para orquestrar.

| Camada | Prefixo | Objeto | Conteúdo |
|---|---|---|---|
| Bronze (staging) | `stg_` | `stg_viagem` | O objeto JSON de cada viagem exatamente como a API devolveu (`payload` jsonb), mais `id`, janela de origem, `hash_registro`, `carregado_em`, `atualizado_em`. Sem tratamento |
| Silver (intermediária) | `int_` | `int_viagem` | Colunas tipadas extraídas do payload (datas, valores, órgão, UG, beneficiário, situação) e derivadas (`dias_afastamento`, `valor_outros_gastos`). Atualizada a cada viagem nova ou alterada |
| Gold (analítica) | `dim_`, `fct_`, `obt_` | `fct_viagem`; `dim_data`, `dim_orgao`, `dim_ug`, `dim_beneficiario`, `dim_perfil_viagem`; `obt_viagem` | Modelo dimensional e one big table. A fato tem uma linha por viagem. A `obt_viagem` junta fato e dimensões numa única visão para BI direto |
| Controle | `ctl_`, `vw_ctl_` | `ctl_janela`, `ctl_execucao`, `vw_ctl_pendencias`, `vw_ctl_tardios` | Uma linha por janela (órgão × mês de ida × mês de retorno) com status e conciliação; histórico de execuções |

Regras: a staging nunca recebe regra de negócio; a intermediária pode ser reconstruída inteira a partir da staging (`--reconstruir-silver`, sem chamar a API); **todas as cargas são incrementais**: a staging faz upsert por `id` e só grava o que é novo ou mudou (hash); a intermediária é atualizada só para as viagens novas ou alteradas; a analítica é carregada só com as viagens da intermediária alteradas desde a última marca d'água (`ctl_camada`), e uma mudança em dimensão (órgão, UG) atualiza as linhas afetadas da `obt_viagem`. A analítica é formada por tabelas, não visões. Dimensões e fato usam chaves naturais (`orgao_siafi`, `ug_codigo`, datas) e chaves hash para beneficiário e perfil. Uso: Power BI/Metabase/Pentaho podem usar o modelo estrela (`fct_` + `dim_`) ou só `obt_viagem`. Cada camada tem seu schema (já separados e em uso): `staging` (stg_ e ctl_), `intermediaria` (int_) e `analitica` (dim_, fct_, obt_). O destino de cada uma é configurável no `.env` (`SCHEMA_STG`, `SCHEMA_INT`, `SCHEMA_ANA`). DDL em `3-Etl/dags/sql/schema.sql`.

## 10. Estado atual e validações já feitas
- API: chave funcionando; varredura 2026 do órgão 33000 = **1.460 viagens** (Jan 90, Fev 183, Mar 333, Abr 164, Mai 224, Jun 202, Jul 113, Ago 145, Set 6), repetida com o mesmo resultado.
- Integridade (1.460 registros): ids e PCDP únicos, datas completas, fim ≥ início.
- Banco (PostgreSQL 15.12, schema `staging`): carga de teste de ago–set/2026 gravou 151 viagens; releitura seguinte deu 0 novos e 0 alterados; o total do gold para agosto (R$ 556.945,17) bate com o da API.
- Schemas separados em uso (`staging`, `intermediaria`, `analitica`). Teste de registro tardio: uma viagem removida de todas as camadas foi reinserida na janela seguinte (novos=1) e propagada até a `obt_viagem`; com nada novo, a analítica processa 0 viagens.
- **Não validado:** carga completa desde 2025 no banco, `/viagens-por-cpf`, download em lote, detecção de registro tardio em cenário real.

## 10.1 Decisões registradas
| Data | Decisão | Motivo |
|---|---|---|
| 19/10/2026 | O CPF permanece como a API entrega, mascarado (`***.584.117-**`), em todas as camadas. Não há CPF completo em lugar nenhum e não se tenta reconstruí-lo | A API só fornece o CPF parcial; reduz o risco de LGPD |
| 19/10/2026 | O campo `motivo` (texto livre) sai da camada analítica (`fct_viagem` e `obt_viagem`). Continua na intermediária (`int_viagem`) e, como veio, no JSON da staging | Texto livre pode conter dado pessoal; a analítica é a camada de consumo |
| 19/10/2026 | Nome do beneficiário segue na analítica (`dim_beneficiario`, `obt_viagem`) | **Pendente** confirmar (default do Atlas: dado individual fora do gold sem ADR) |

## 10.2 Validação do stack por revisão independente (19/10/2026)
Quatro revisões somente leitura (lógica e arquitetura; segurança e robustez; SQL do PostgreSQL; checagens mecânicas e documentação). O que foi confirmado e corrigido:

| Achado | Correção |
|---|---|
| Duas execuções ao mesmo tempo (DAG diária e completa) podiam perder viagens na marca d'água da analítica | Trava no banco por combinação dos três schemas (`pg_try_advisory_lock`); a segunda execução sai com código 3 (tarefa *skipped* no Airflow) |
| Texto vazio, inválido ou fora do limite no JSON derrubava a janela inteira (confirmado no Postgres) | Funções `f_data`, `f_numero` e `f_inteiro`: valor ruim vira `NULL` na intermediária; o JSON da staging fica intacto. Data só no formato ISO |
| Id repetido entre páginas da API fazia o upsert falhar (confirmado) | Repetidos descartados com aviso |
| Chave da API e senhas podiam ir para logs e para `ctl_erro` | Mascaramento (`***`) em toda mensagem; `Config` não mostra segredos no `repr` |
| Nome de schema vindo do ambiente entrava no SQL sem validação | Validação por expressão regular |
| Queda de conexão derrubava o tratamento de erro | Vira erro fatal registrado; a execução termina com código 1 |
| Resposta 200 que não é JSON, `Retry-After` em formato de data, 403 e 404 | Repetida, tratada com padrão e teto, e tratados como erro permanente (401 e 403 abortam) |
| `schema.sql` pedia lock exclusivo a cada execução | `lock_timeout`, trava de DDL e coluna criada só se faltar |
| README divergente do código | Corrigido |

Pendências conhecidas, sem correção por decisão ou dependência: DAGs duplicadas e agendamento (fuso, intervalo de 10 dias, pool, segredos), conciliação que só compara a API com o que acabou de gravar (não detecta página intermediária vazia por instabilidade), `UPDATE` sem `WHERE` nas tabelas fato e `obt`, chave de beneficiário por nome + CPF parcial (homônimos), `dim_data` só até 2030 e actions do CI fixadas por tag.

## 10.3 Segunda rodada de validação (19/10/2026)
Mesmos quatro revisores sobre o código já corrigido. Todas as correções da primeira rodada foram confirmadas. Achados novos, corrigidos:

| Achado | Correção |
|---|---|
| A mascaragem de segredos falhava com senha curta dentro da chave, senha com `%` na URL e DSN em formato chave-valor; o corpo de erro era cortado antes de mascarar | Segredos ordenados do maior para o menor e decodificados; mascarar antes de cortar |
| Paginação podia girar para sempre (API que ignora `pagina` ou devolve um objeto) | Para se a página se repetir, se não for lista ou se passar de 1.000 páginas |
| O `requests` seguia redirecionamentos reenviando o cabeçalho com a chave | Sem redirecionamento; 3xx é erro permanente; `https://` obrigatório |
| Mensagem de erro do PostgreSQL trazia o `DETAIL` com dado pessoal | Só a mensagem principal vai para log e `ctl_erro` |
| Marcadores `@INT@`/`@STG@` eram trocados também dentro dos dados gravados | A troca é feita só no texto do SQL |
| `aplicar_schema` rodava antes da trava, a cada execução, com lock de DDL | Roda com a trava em mãos e só quando o `schema.sql` muda (hash em `ctl_schema`) |
| A trava era por órgão, mas a marca d'água e o controle são globais | Trava por conjunto de schemas |
| Código 3 virava falha no Airflow; erro permanente (400/404) era repetido nas rodadas extras | `skip_on_exit_code=3`; janela com erro permanente não é repetida |
| Execução morta ficava `EXECUTANDO` por 12 h | Com a trava em mãos, é marcada `INTERROMPIDA` na hora; `SIGTERM` também finaliza a execução |
| Conversão tolerante zerava dados sem avisar | Aviso por janela com a quantidade; arredondamento explícito de `numeric` |
| Analítica reprocessava tudo a cada execução depois de uma reconstrução (empate no `>=` da marca d'água) | Filtro `>`, seguro porque só um escritor roda por vez |
| DAGs: fuso UTC, `*/10` nos dias 1/11/21/31, caminho sem aspas, código duplicado | `America/Sao_Paulo`, `schedule=timedelta(days=10)`, `shlex.quote`, comando montado em `scdp/dag_util.py`, `.airflowignore` |

Pendências conhecidas: conciliação que só compara a API com o que acabou de gravar, `UPDATE` sem `WHERE` nas tabelas fato e `obt`, chave de beneficiário por nome + CPF parcial, `dim_data` só até 2030, actions do CI por tag, segredos das DAGs via ambiente do worker (sem Connections/Variables do Airflow) e `CREATE OR REPLACE VIEW` com colunas explícitas (colunas novas só no fim).

## 10.4 Terceira rodada de validação (19/10/2026)
Nenhum achado alto. Todas as correções da segunda rodada foram confirmadas. Corrigido nesta rodada:

| Achado | Correção |
|---|---|
| `schedule=timedelta(days=10)` no Airflow 2.10 não mantém o horário 03:30 | Cron `30 3 1,11,21 * *` em `America/Sao_Paulo` |
| A completa podia ser pulada em silêncio (código 3 vira *skipped*) | `skip_on_exit_code` só na diária; na completa o código 3 falha e o retry tenta de novo |
| O hash do schema ignorava `SCHEMA_INT` e `SCHEMA_ANA` | Hash do texto já com os nomes dos schemas resolvidos |
| A trava considerava só `SCHEMA_STG` | Chave com os três schemas |
| `f_numero` testava o limite antes de arredondar (9999999999999.995 estourava `numeric(15,2)`) | Arredonda antes de testar o limite |
| `message_primary` do PostgreSQL ainda trazia o valor ofensivo (`... bigint: "FULANO"`) | Mensagem cortada antes do valor; teste com erro real de cast |
| Erro de banco no meio da execução deixava `EXECUTANDO` | Fecha como `ABORTADA` |
| Comando da DAG lia o ambiente no parse (scheduler), não no worker | O bash resolve `PAINEL_SCDP_HOME` e `PAINEL_SCDP_PYTHON` na hora de rodar |
| `SIGTERM` terminava com traceback | Código 143, execução marcada `INTERROMPIDA` |
| Schema com nome reservado ou `pg_*`; `DATABASE_URL` inválida | Recusados com erro claro, sem eco da senha |
| CI sem timeout e testes de banco podiam ser pulados em silêncio | `timeout-minutes` e `REQUIRE_DB_TESTS=1` (falha se faltar o banco de teste); a fixture limpa os schemas se o preparo falhar |
| Falta de índice em `int_viagem(atualizado_em)` | Criado |

Observação operacional (confirmada na validação real): a trava é de sessão. Uma execução manual recebeu código 3 enquanto outra sessão do mesmo usuário (execução 27) rodava, como projetado. Se um worker morrer sem fechar a conexão, a trava só sai quando o servidor perceber a sessão morta. O `schema.sql` também exige que os três schemas já existam.

Pendências conhecidas: conciliação que só compara a API com o que acabou de gravar, `UPDATE` sem `WHERE` nas tabelas fato e `obt`, chave de beneficiário por nome + CPF parcial, `dim_data` só até 2030, actions do CI por tag, segredos das DAGs via ambiente do worker, relógio do servidor que recue (poderia perder linhas na marca d'água; mitigação: `--reconstruir-silver` periódico) e retentativa da DAG repetindo a varredura quando sobra erro permanente.

## 11. Riscos
| Risco | Mitigação |
|---|---|
| Escopo de órgão errado (perder INSS) | Decisão 5.1 antes da carga final |
| Registros que chegam com atraso | Releitura diária das janelas recentes e completa a cada 10 dias, com `TARDIO` |
| Instabilidade da API (504, vazio transitório) | Retry, releitura de janelas com queda de contagem, `ctl_janela` |
| Suspensão do token por excesso de uso | Uso de 50% do limite, pausa por horário, tratamento de 429 |
| Viagens sem data de retorno ficam invisíveis na API | Avaliar o download em lote como fonte complementar |
| Dado sigiloso ou CPF mascarado impede identificar o viajante | Agrupar por nome + CPF parcial; reconhecer o limite |
| Código `308819` sem origem conhecida | Esclarecer com a área de negócio |

## 12. Plano em fases
1. **Fase 1 (pronta, falta validar em banco):** carga diária/completa de um órgão com controle.
2. **Fase 2:** decidir escopo de órgãos; adaptar a lista de órgãos; validar a carga em Postgres real; agendar as tarefas.
3. **Fase 3:** avaliar o download em lote (histórico completo, trechos, passagens, pagamentos) e conciliar com a API.
4. **Fase 4:** painel e, se desejado, enriquecimento com `/servidores` (nome + CPF mascarado).

## 13. Arquivos do projeto
Padrão de pastas dos demais projetos: `1-Documentos` (PRD, `referencia_api.md`, `referencia/orgaos_siafi.csv` e `orgaos_siape.csv`), `2-Scripts` (`consulta_viagens.py`, `varredura_2026.py`, `postman/`, `saidas/` não versionada), `3-Etl/dags` (DAGs, `carga_viagens.py` como ponto de entrada, pacote `scdp/` com `extracao`, `carga`, `transformacao`, `controle`, `janelas`, `pipeline`, `config` e `cli`, e `sql/schema.sql`), `tests/` (unitários e de integração), `4-DataViz`, `5-Images`. Na raiz: `README.md`, `.env` (segredos, fora do git), `.env.example`, `.gitignore` e `CLAUDE.md` (instruções locais do Claude Code, também fora do git).
