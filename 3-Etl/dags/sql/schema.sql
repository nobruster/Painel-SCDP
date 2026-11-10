-- Serializa o DDL entre execucoes simultaneas e evita esperar lock indefinidamente.
SET LOCAL lock_timeout = '15s';
SELECT pg_advisory_xact_lock(727274);

-- STAGING (bronze): JSON exatamente como recebido da API, sem tratamento.
CREATE TABLE IF NOT EXISTS @STG@.stg_viagem (
    id              bigint      PRIMARY KEY,
    janela_ida      date        NOT NULL,
    janela_retorno  date        NOT NULL,
    payload         jsonb       NOT NULL,
    hash_registro   text        NOT NULL,
    carregado_em    timestamptz NOT NULL DEFAULT now(),
    atualizado_em   timestamptz NOT NULL DEFAULT now()
);

-- INTERMEDIATE (silver): dados tipados e derivados a partir da staging.
CREATE TABLE IF NOT EXISTS @INT@.int_viagem (
    id                      bigint PRIMARY KEY,
    janela_ida              date,
    janela_retorno          date,
    pcdp                    text,
    num_pcdp                text,
    ano                     int,
    situacao                text,
    tipo_viagem             text,
    urgencia_viagem         text,
    beneficiario_nome       text,
    cpf_mascarado           text,
    orgao_siafi             text,
    orgao_nome              text,
    orgao_sigla             text,
    orgao_maximo_sigla      text,
    ug_codigo               text,
    ug_nome                 text,
    data_inicio             date,
    data_fim                date,
    dias_afastamento        int,
    valor_total_viagem      numeric(15,2),
    valor_passagem          numeric(15,2),
    valor_diarias           numeric(15,2),
    valor_taxa_agenciamento numeric(15,2),
    valor_restituicao       numeric(15,2),
    valor_devolucao         numeric(15,2),
    valor_multa             numeric(15,2),
    valor_outros_gastos     numeric(15,2),
    motivo                  text,
    atualizado_em           timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_int_viagem_inicio ON @INT@.int_viagem (data_inicio);
CREATE INDEX IF NOT EXISTS ix_int_viagem_orgao ON @INT@.int_viagem (orgao_siafi, data_inicio);
CREATE INDEX IF NOT EXISTS ix_int_viagem_atualizado ON @INT@.int_viagem (atualizado_em);

-- CONTROLE
CREATE TABLE IF NOT EXISTS @STG@.ctl_janela (
    orgao          text        NOT NULL,
    ida_mes        date        NOT NULL,
    retorno_mes    date        NOT NULL,
    status         text        NOT NULL,
    paginas_lidas  int,
    qtd_api        int,
    qtd_carregada  int,
    qtd_novos      int,
    qtd_alterados  int,
    tentativas     int         NOT NULL DEFAULT 0,
    aviso          text,
    erro           text,
    inicio         timestamptz,
    fim            timestamptz,
    PRIMARY KEY (orgao, ida_mes, retorno_mes)
);

CREATE TABLE IF NOT EXISTS @STG@.ctl_execucao (
    id             bigserial PRIMARY KEY,
    inicio         timestamptz NOT NULL DEFAULT now(),
    fim            timestamptz,
    modo           text,
    janelas_total  int,
    janelas_lidas  int,
    janelas_erro   int,
    novos          int,
    alterados      int,
    status         text
);

-- Erros abertos: uma linha por (janela, etapa). Sai desta tabela quando o erro e corrigido (vai para o historico).
CREATE TABLE IF NOT EXISTS @STG@.ctl_erro (
    chave               text PRIMARY KEY,
    orgao               text,
    ida_mes             date,
    retorno_mes         date,
    etapa               text NOT NULL,
    codigo              text,
    mensagem            text,
    tentativas          int NOT NULL DEFAULT 1,
    primeira_ocorrencia timestamptz NOT NULL DEFAULT now(),
    ultima_ocorrencia   timestamptz NOT NULL DEFAULT now(),
    execucao_id         bigint
);

CREATE TABLE IF NOT EXISTS @STG@.ctl_erro_historico (
    id                    bigserial PRIMARY KEY,
    chave                 text,
    orgao                 text,
    ida_mes               date,
    retorno_mes           date,
    etapa                 text,
    codigo                text,
    mensagem              text,
    tentativas            int,
    primeira_ocorrencia   timestamptz,
    ultima_ocorrencia     timestamptz,
    execucao_id           bigint,
    resolvido_em          timestamptz NOT NULL DEFAULT now(),
    resolvido_na_execucao bigint
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = '@STG@' AND table_name = 'ctl_execucao' AND column_name = 'status') THEN
        ALTER TABLE @STG@.ctl_execucao ADD COLUMN status text;
    END IF;
END $$;

CREATE OR REPLACE VIEW @STG@.vw_ctl_pendencias AS
SELECT orgao, ida_mes, retorno_mes, status, paginas_lidas, qtd_api, qtd_carregada, qtd_novos, qtd_alterados,
       tentativas, aviso, erro, inicio, fim
FROM @STG@.ctl_janela WHERE status <> 'OK' OR qtd_api IS DISTINCT FROM qtd_carregada;

CREATE OR REPLACE VIEW @STG@.vw_ctl_tardios AS
SELECT b.id, s.data_inicio, s.data_fim, b.janela_ida, b.janela_retorno, b.carregado_em
FROM @STG@.stg_viagem b
JOIN @INT@.int_viagem s USING (id)
WHERE s.data_inicio < date_trunc('month', current_date) - interval '3 months'
  AND b.carregado_em > now() - interval '2 days'
  AND b.carregado_em > (SELECT min(inicio) FROM @STG@.ctl_execucao) + interval '1 day';

-- Marca d'agua da ultima carga incremental de cada camada derivada.
CREATE TABLE IF NOT EXISTS @STG@.ctl_camada (
    camada         text PRIMARY KEY,
    marca          timestamptz,
    linhas         int,
    atualizado_em  timestamptz NOT NULL DEFAULT now()
);

-- Versao do schema aplicada (hash do arquivo): o DDL so roda de novo quando o arquivo muda.
CREATE TABLE IF NOT EXISTS @STG@.ctl_schema (
    id            int PRIMARY KEY CHECK (id = 1),
    versao        text NOT NULL,
    aplicado_em   timestamptz NOT NULL DEFAULT now()
);

-- Observabilidade (schema staging): erros abertos, execucoes e resumo de saude da carga.
CREATE OR REPLACE VIEW @STG@.vw_ctl_erros_abertos AS
SELECT chave, orgao, ida_mes, retorno_mes, etapa, codigo, mensagem, tentativas,
       primeira_ocorrencia, ultima_ocorrencia,
       round(extract(epoch FROM (now() - primeira_ocorrencia)) / 3600.0, 1) AS horas_aberto,
       execucao_id
FROM @STG@.ctl_erro;

CREATE OR REPLACE VIEW @STG@.vw_ctl_execucoes AS
SELECT id, modo, status, inicio, fim,
       round(extract(epoch FROM (coalesce(fim, now()) - inicio)) / 60.0, 1) AS minutos,
       janelas_total, janelas_lidas, janelas_erro, novos, alterados
FROM @STG@.ctl_execucao;

CREATE OR REPLACE VIEW @STG@.vw_ctl_saude AS
SELECT
  (SELECT count(*) FROM @STG@.ctl_janela)                                         AS janelas_total,
  (SELECT count(*) FROM @STG@.ctl_janela WHERE status = 'OK')                     AS janelas_ok,
  (SELECT count(*) FROM @STG@.ctl_janela WHERE status <> 'OK')                    AS janelas_pendentes,
  (SELECT count(*) FROM @STG@.ctl_erro)                                           AS erros_abertos,
  (SELECT count(*) FROM @STG@.ctl_erro_historico)                                 AS erros_resolvidos,
  (SELECT sum(qtd_api) FROM @STG@.ctl_janela)                                     AS registros_api,
  (SELECT sum(qtd_carregada) FROM @STG@.ctl_janela)                               AS registros_carregados,
  (SELECT status FROM @STG@.ctl_execucao ORDER BY id DESC LIMIT 1)                AS ultima_execucao_status,
  (SELECT fim FROM @STG@.ctl_execucao ORDER BY id DESC LIMIT 1)                   AS ultima_execucao_fim,
  (SELECT max(fim) FROM @STG@.ctl_execucao WHERE status = 'CONCLUIDA')            AS ultima_execucao_concluida,
  (SELECT marca FROM @STG@.ctl_camada WHERE camada = 'analitica')                 AS marca_analitica;

-- ANALITICA (gold): tabelas dimensionais (dim_*), fato (fct_*) e one big table (obt_*), carga incremental.
CREATE TABLE IF NOT EXISTS @ANA@.dim_data (
    data_key       date PRIMARY KEY,
    ano            int,
    trimestre      int,
    mes            int,
    ano_mes        text,
    dia_semana     int,
    fim_de_semana  boolean
);
INSERT INTO @ANA@.dim_data (data_key, ano, trimestre, mes, ano_mes, dia_semana, fim_de_semana)
SELECT d::date, extract(year FROM d)::int, extract(quarter FROM d)::int, extract(month FROM d)::int,
       to_char(d, 'YYYY-MM'), extract(isodow FROM d)::int, extract(isodow FROM d) IN (6, 7)
FROM generate_series('2020-01-01'::timestamp, '2030-12-31'::timestamp, interval '1 day') AS d
ON CONFLICT (data_key) DO NOTHING;

CREATE TABLE IF NOT EXISTS @ANA@.dim_orgao (
    orgao_siafi         text PRIMARY KEY,
    orgao_nome          text,
    orgao_sigla         text,
    orgao_maximo_sigla  text,
    atualizado_em       timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS @ANA@.dim_ug (
    ug_codigo      text PRIMARY KEY,
    ug_nome        text,
    atualizado_em  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS @ANA@.dim_beneficiario (
    beneficiario_key   text PRIMARY KEY,
    beneficiario_nome  text,
    cpf_mascarado      text,
    atualizado_em      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS @ANA@.dim_perfil_viagem (
    perfil_key       text PRIMARY KEY,
    situacao         text,
    tipo_viagem      text,
    urgencia_viagem  text,
    atualizado_em    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS @ANA@.fct_viagem (
    viagem_id               bigint PRIMARY KEY,
    pcdp                    text,
    num_pcdp                text,
    data_inicio_key         date,
    data_fim_key            date,
    orgao_siafi             text,
    ug_codigo               text,
    beneficiario_key        text,
    perfil_key              text,
    dias_afastamento        int,
    valor_total_viagem      numeric(15,2),
    valor_passagem          numeric(15,2),
    valor_diarias           numeric(15,2),
    valor_taxa_agenciamento numeric(15,2),
    valor_restituicao       numeric(15,2),
    valor_devolucao         numeric(15,2),
    valor_multa             numeric(15,2),
    valor_outros_gastos     numeric(15,2),
    atualizado_em           timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_fct_viagem_inicio ON @ANA@.fct_viagem (data_inicio_key);
CREATE INDEX IF NOT EXISTS ix_fct_viagem_orgao ON @ANA@.fct_viagem (orgao_siafi);
CREATE INDEX IF NOT EXISTS ix_fct_viagem_ug ON @ANA@.fct_viagem (ug_codigo);

CREATE TABLE IF NOT EXISTS @ANA@.obt_viagem (
    viagem_id               bigint PRIMARY KEY,
    pcdp                    text,
    num_pcdp                text,
    data_inicio             date,
    data_fim                date,
    ano_inicio              int,
    mes_inicio              int,
    ano_mes_inicio          text,
    trimestre_inicio        int,
    orgao_siafi             text,
    orgao_nome              text,
    orgao_sigla             text,
    orgao_maximo_sigla      text,
    ug_codigo               text,
    ug_nome                 text,
    beneficiario_nome       text,
    cpf_mascarado           text,
    situacao                text,
    tipo_viagem             text,
    urgencia_viagem         text,
    dias_afastamento        int,
    valor_total_viagem      numeric(15,2),
    valor_passagem          numeric(15,2),
    valor_diarias           numeric(15,2),
    valor_taxa_agenciamento numeric(15,2),
    valor_restituicao       numeric(15,2),
    valor_devolucao         numeric(15,2),
    valor_multa             numeric(15,2),
    valor_outros_gastos     numeric(15,2),
    atualizado_em           timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_obt_viagem_mes ON @ANA@.obt_viagem (ano_mes_inicio);
CREATE INDEX IF NOT EXISTS ix_obt_viagem_orgao ON @ANA@.obt_viagem (orgao_siafi);

-- Conversoes tolerantes: texto vazio, invalido ou fora do limite de numeric(15,2) viram NULL em vez de derrubar a janela.
-- O JSON original continua intacto na staging.
CREATE OR REPLACE FUNCTION @INT@.f_data(t text) RETURNS date LANGUAGE plpgsql STABLE AS $$
BEGIN
    IF t IS NULL OR btrim(t) !~ '^\d{4}-\d{2}-\d{2}' THEN
        RETURN NULL;
    END IF;
    RETURN btrim(t)::date;
EXCEPTION WHEN others THEN
    RETURN NULL;
END $$;

CREATE OR REPLACE FUNCTION @INT@.f_numero(t text) RETURNS numeric LANGUAGE plpgsql STABLE AS $$
DECLARE v numeric;
BEGIN
    v := round(nullif(btrim(t), '')::numeric, 2);
    IF v IS NULL OR v >= 10000000000000 OR v <= -10000000000000 THEN
        RETURN NULL;
    END IF;
    RETURN v;
EXCEPTION WHEN others THEN
    RETURN NULL;
END $$;

CREATE OR REPLACE FUNCTION @INT@.f_inteiro(t text) RETURNS int LANGUAGE plpgsql STABLE AS $$
BEGIN
    RETURN nullif(btrim(t), '')::int;
EXCEPTION WHEN others THEN
    RETURN NULL;
END $$;

-- DESCRICAO DOS OBJETOS (COMMENT ON): documenta cada tabela, view e coluna no proprio banco.
COMMENT ON TABLE @STG@.stg_viagem IS 'Staging (bronze): JSON de cada viagem exatamente como a API /viagens devolveu, sem regra de negócio. Uma linha por id.';
COMMENT ON COLUMN @STG@.stg_viagem.id IS 'Id da viagem na API (campo id da lista; usado em /viagens/{id}).';
COMMENT ON COLUMN @STG@.stg_viagem.janela_ida IS 'Primeiro dia do mês de ida da janela em que a viagem foi lida.';
COMMENT ON COLUMN @STG@.stg_viagem.janela_retorno IS 'Primeiro dia do mês de retorno da janela em que a viagem foi lida.';
COMMENT ON COLUMN @STG@.stg_viagem.payload IS 'JSON original da viagem, intacto.';
COMMENT ON COLUMN @STG@.stg_viagem.hash_registro IS 'Hash do payload; a carga só regrava a viagem quando o hash muda.';
COMMENT ON COLUMN @STG@.stg_viagem.carregado_em IS 'Quando a viagem entrou na staging pela primeira vez.';
COMMENT ON COLUMN @STG@.stg_viagem.atualizado_em IS 'Última vez em que o payload foi regravado por alteração.';

COMMENT ON TABLE @INT@.int_viagem IS 'Intermediária (silver): viagem tipada e derivada a partir da staging. Uma linha por id; conversões tolerantes (valor inválido vira NULL).';
COMMENT ON COLUMN @INT@.int_viagem.pcdp IS 'Número da proposta de concessão de diárias e passagens (único; só existe a partir de 2020).';
COMMENT ON COLUMN @INT@.int_viagem.num_pcdp IS 'PCDP no formato número/ano (ex.: 001736/26); pode ter complemento (-1C) ou o texto de sigilo.';
COMMENT ON COLUMN @INT@.int_viagem.situacao IS 'Realizada ou Não realizada (viagem cancelada continua aparecendo).';
COMMENT ON COLUMN @INT@.int_viagem.tipo_viagem IS 'Nacional ou Internacional.';
COMMENT ON COLUMN @INT@.int_viagem.urgencia_viagem IS 'Sim, Não ou Sigiloso (só existe a partir de 2020).';
COMMENT ON COLUMN @INT@.int_viagem.beneficiario_nome IS 'Nome do viajante; "Informações protegidas por sigilo" nas viagens sigilosas.';
COMMENT ON COLUMN @INT@.int_viagem.cpf_mascarado IS 'CPF como a API entrega, mascarado (***.947.711-**). Não serve de chave de pesquisa.';
COMMENT ON COLUMN @INT@.int_viagem.orgao_siafi IS 'Código SIAFI (5 dígitos) do órgão solicitante; é o filtro codigoOrgao da API.';
COMMENT ON COLUMN @INT@.int_viagem.orgao_nome IS 'Nome do órgão solicitante.';
COMMENT ON COLUMN @INT@.int_viagem.orgao_sigla IS 'Sigla do órgão solicitante.';
COMMENT ON COLUMN @INT@.int_viagem.orgao_maximo_sigla IS 'Sigla do órgão superior (ministério).';
COMMENT ON COLUMN @INT@.int_viagem.ug_codigo IS 'Código da unidade gestora responsável; -1 e -11 são códigos sem UG real.';
COMMENT ON COLUMN @INT@.int_viagem.ug_nome IS 'Nome da unidade gestora responsável.';
COMMENT ON COLUMN @INT@.int_viagem.dias_afastamento IS 'Derivado: dias entre início e fim, contando os dois extremos.';
COMMENT ON COLUMN @INT@.int_viagem.atualizado_em IS 'Última vez em que a linha foi gravada ou alterada; base da marca d''água da analítica.';
COMMENT ON COLUMN @INT@.int_viagem.valor_total_viagem IS 'Valor total da viagem (R$): diárias + passagem + taxa + restituição + outros gastos.';
COMMENT ON COLUMN @INT@.int_viagem.valor_passagem IS 'Valor das passagens (R$).';
COMMENT ON COLUMN @INT@.int_viagem.valor_diarias IS 'Valor das diárias (R$).';
COMMENT ON COLUMN @INT@.int_viagem.valor_taxa_agenciamento IS 'Taxa de agenciamento (R$); zero no MPS.';
COMMENT ON COLUMN @INT@.int_viagem.valor_restituicao IS 'Restituição (R$); entra somada no total.';
COMMENT ON COLUMN @INT@.int_viagem.valor_devolucao IS 'Devolução (R$); não entra no total.';
COMMENT ON COLUMN @INT@.int_viagem.valor_multa IS 'Multa (R$); zero em todas as viagens observadas.';
COMMENT ON COLUMN @INT@.int_viagem.valor_outros_gastos IS 'Outros gastos (R$): total menos passagem, diárias, taxa e restituição. A API não expõe esse campo.';
COMMENT ON COLUMN @INT@.int_viagem.id IS 'Id da viagem na API.';
COMMENT ON COLUMN @INT@.int_viagem.janela_ida IS 'Mês de ida da janela em que a viagem foi lida.';
COMMENT ON COLUMN @INT@.int_viagem.janela_retorno IS 'Mês de retorno da janela em que a viagem foi lida.';
COMMENT ON COLUMN @INT@.int_viagem.ano IS 'Ano da PCDP.';
COMMENT ON COLUMN @INT@.int_viagem.data_inicio IS 'Início do afastamento (dataInicioAfastamento).';
COMMENT ON COLUMN @INT@.int_viagem.data_fim IS 'Fim do afastamento (dataFimAfastamento); sempre maior ou igual ao início.';
COMMENT ON COLUMN @INT@.int_viagem.motivo IS 'Motivo da viagem em texto livre (não segue para a analítica).';

COMMENT ON TABLE @STG@.ctl_janela IS 'Controle: uma linha por janela de consulta (órgão, mês de ida, mês de retorno) com o resultado da última leitura.';
COMMENT ON COLUMN @STG@.ctl_janela.orgao IS 'Código SIAFI consultado.';
COMMENT ON COLUMN @STG@.ctl_janela.ida_mes IS 'Primeiro dia do mês de ida da janela.';
COMMENT ON COLUMN @STG@.ctl_janela.retorno_mes IS 'Primeiro dia do mês de retorno da janela.';
COMMENT ON COLUMN @STG@.ctl_janela.status IS 'OK quando a janela foi lida e conferida; qualquer outro valor é pendência.';
COMMENT ON COLUMN @STG@.ctl_janela.paginas_lidas IS 'Páginas lidas na API até vir a página vazia.';
COMMENT ON COLUMN @STG@.ctl_janela.qtd_api IS 'Registros devolvidos pela API na janela.';
COMMENT ON COLUMN @STG@.ctl_janela.qtd_carregada IS 'Registros da janela presentes na staging após a carga; deve ser igual a qtd_api.';
COMMENT ON COLUMN @STG@.ctl_janela.qtd_novos IS 'Viagens novas na staging nesta leitura.';
COMMENT ON COLUMN @STG@.ctl_janela.qtd_alterados IS 'Viagens que já existiam e mudaram (hash diferente) nesta leitura.';
COMMENT ON COLUMN @STG@.ctl_janela.tentativas IS 'Quantas vezes a janela foi tentada.';
COMMENT ON COLUMN @STG@.ctl_janela.aviso IS 'Observação que não impede a carga.';
COMMENT ON COLUMN @STG@.ctl_janela.erro IS 'Mensagem do último erro da janela.';
COMMENT ON COLUMN @STG@.ctl_janela.inicio IS 'Início da última leitura da janela.';
COMMENT ON COLUMN @STG@.ctl_janela.fim IS 'Fim da última leitura da janela.';

COMMENT ON TABLE @STG@.ctl_execucao IS 'Controle: uma linha por execução da carga (diária ou completa).';
COMMENT ON COLUMN @STG@.ctl_execucao.id IS 'Número da execução.';
COMMENT ON COLUMN @STG@.ctl_execucao.inicio IS 'Início da execução.';
COMMENT ON COLUMN @STG@.ctl_execucao.fim IS 'Fim da execução; nulo enquanto roda ou se foi interrompida.';
COMMENT ON COLUMN @STG@.ctl_execucao.modo IS 'Modo da execução (diario, completo ou reconstruir-silver).';
COMMENT ON COLUMN @STG@.ctl_execucao.janelas_total IS 'Janelas planejadas para a execução.';
COMMENT ON COLUMN @STG@.ctl_execucao.janelas_lidas IS 'Janelas lidas com sucesso.';
COMMENT ON COLUMN @STG@.ctl_execucao.janelas_erro IS 'Janelas que terminaram com erro.';
COMMENT ON COLUMN @STG@.ctl_execucao.novos IS 'Viagens novas gravadas na staging.';
COMMENT ON COLUMN @STG@.ctl_execucao.alterados IS 'Viagens alteradas na staging.';
COMMENT ON COLUMN @STG@.ctl_execucao.status IS 'Situação da execução (em execução, concluída, com erros ou interrompida).';

COMMENT ON TABLE @STG@.ctl_erro IS 'Controle: erros abertos, uma linha por janela e etapa. A linha sai daqui (vai para ctl_erro_historico) quando o erro é corrigido.';
COMMENT ON COLUMN @STG@.ctl_erro.chave IS 'Identificador do erro: janela mais etapa.';
COMMENT ON COLUMN @STG@.ctl_erro.orgao IS 'Código SIAFI da janela com erro.';
COMMENT ON COLUMN @STG@.ctl_erro.ida_mes IS 'Mês de ida da janela com erro.';
COMMENT ON COLUMN @STG@.ctl_erro.retorno_mes IS 'Mês de retorno da janela com erro.';
COMMENT ON COLUMN @STG@.ctl_erro.etapa IS 'Etapa em que falhou (extração, staging, intermediária ou analítica).';
COMMENT ON COLUMN @STG@.ctl_erro.codigo IS 'Código do erro (HTTP ou interno).';
COMMENT ON COLUMN @STG@.ctl_erro.mensagem IS 'Mensagem do erro, sem dados sensíveis.';
COMMENT ON COLUMN @STG@.ctl_erro.tentativas IS 'Quantas vezes o erro se repetiu.';
COMMENT ON COLUMN @STG@.ctl_erro.primeira_ocorrencia IS 'Quando o erro apareceu pela primeira vez.';
COMMENT ON COLUMN @STG@.ctl_erro.ultima_ocorrencia IS 'Última vez em que o erro se repetiu.';
COMMENT ON COLUMN @STG@.ctl_erro.execucao_id IS 'Execução (ctl_execucao.id) em que ocorreu por último.';

COMMENT ON TABLE @STG@.ctl_erro_historico IS 'Controle: erros já corrigidos, movidos de ctl_erro.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.id IS 'Identificador da linha do histórico.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.chave IS 'Chave que o erro tinha em ctl_erro.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.orgao IS 'Código SIAFI da janela.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.ida_mes IS 'Mês de ida da janela.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.retorno_mes IS 'Mês de retorno da janela.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.etapa IS 'Etapa em que o erro ocorreu.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.codigo IS 'Código do erro.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.mensagem IS 'Mensagem do erro.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.tentativas IS 'Tentativas até o erro ser resolvido.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.primeira_ocorrencia IS 'Quando o erro apareceu pela primeira vez.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.ultima_ocorrencia IS 'Última ocorrência antes de ser resolvido.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.execucao_id IS 'Última execução em que o erro ocorreu.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.resolvido_em IS 'Quando o erro foi dado como resolvido.';
COMMENT ON COLUMN @STG@.ctl_erro_historico.resolvido_na_execucao IS 'Execução que resolveu o erro.';

COMMENT ON TABLE @STG@.ctl_camada IS 'Controle: marca d''água da última carga incremental da camada analítica (staging e intermediária se controlam por hash e por viagens novas ou alteradas).';
COMMENT ON COLUMN @STG@.ctl_camada.camada IS 'Camada controlada (analitica).';
COMMENT ON COLUMN @STG@.ctl_camada.marca IS 'Maior atualizado_em da int_viagem já processado; a próxima carga lê só o que for maior.';
COMMENT ON COLUMN @STG@.ctl_camada.linhas IS 'Linhas processadas na última carga; zero quando não havia novidade.';
COMMENT ON COLUMN @STG@.ctl_camada.atualizado_em IS 'Quando a camada foi verificada pela última vez.';

COMMENT ON TABLE @STG@.ctl_schema IS 'Controle: versão (hash) do schema.sql aplicado; o DDL só roda de novo quando o arquivo muda.';
COMMENT ON COLUMN @STG@.ctl_schema.id IS 'Sempre 1 (linha única).';
COMMENT ON COLUMN @STG@.ctl_schema.versao IS 'Hash do schema.sql já com os nomes dos schemas resolvidos.';
COMMENT ON COLUMN @STG@.ctl_schema.aplicado_em IS 'Quando o DDL foi aplicado.';

COMMENT ON TABLE @ANA@.dim_data IS 'Dimensão calendário (2020 a 2030), uma linha por dia.';
COMMENT ON COLUMN @ANA@.dim_data.data_key IS 'Data; chave da dimensão.';
COMMENT ON COLUMN @ANA@.dim_data.ano IS 'Ano.';
COMMENT ON COLUMN @ANA@.dim_data.trimestre IS 'Trimestre (1 a 4).';
COMMENT ON COLUMN @ANA@.dim_data.mes IS 'Mês (1 a 12).';
COMMENT ON COLUMN @ANA@.dim_data.ano_mes IS 'Ano e mês no formato YYYY-MM.';
COMMENT ON COLUMN @ANA@.dim_data.dia_semana IS 'Dia da semana ISO (1 = segunda, 7 = domingo).';
COMMENT ON COLUMN @ANA@.dim_data.fim_de_semana IS 'Verdadeiro para sábado e domingo.';

COMMENT ON TABLE @ANA@.dim_orgao IS 'Dimensão de órgão solicitante da viagem.';
COMMENT ON COLUMN @ANA@.dim_orgao.orgao_siafi IS 'Código SIAFI (5 dígitos) do órgão solicitante; é o filtro codigoOrgao da API.';
COMMENT ON COLUMN @ANA@.dim_orgao.orgao_nome IS 'Nome do órgão solicitante.';
COMMENT ON COLUMN @ANA@.dim_orgao.orgao_sigla IS 'Sigla do órgão solicitante.';
COMMENT ON COLUMN @ANA@.dim_orgao.orgao_maximo_sigla IS 'Sigla do órgão superior (ministério).';
COMMENT ON COLUMN @ANA@.dim_orgao.atualizado_em IS 'Última vez em que a linha foi gravada ou alterada.';

COMMENT ON TABLE @ANA@.dim_ug IS 'Dimensão de unidade gestora responsável pela viagem.';
COMMENT ON COLUMN @ANA@.dim_ug.ug_codigo IS 'Código da unidade gestora responsável; -1 e -11 são códigos sem UG real.';
COMMENT ON COLUMN @ANA@.dim_ug.ug_nome IS 'Nome da unidade gestora responsável.';
COMMENT ON COLUMN @ANA@.dim_ug.atualizado_em IS 'Última vez em que a linha foi gravada ou alterada.';

COMMENT ON TABLE @ANA@.dim_beneficiario IS 'Dimensão de beneficiário (viajante). O CPF segue mascarado como a API entrega.';
COMMENT ON COLUMN @ANA@.dim_beneficiario.beneficiario_key IS 'Chave da dimensão, derivada de nome e CPF mascarado.';
COMMENT ON COLUMN @ANA@.dim_beneficiario.beneficiario_nome IS 'Nome do viajante; "Informações protegidas por sigilo" nas viagens sigilosas.';
COMMENT ON COLUMN @ANA@.dim_beneficiario.cpf_mascarado IS 'CPF como a API entrega, mascarado (***.947.711-**). Não serve de chave de pesquisa.';
COMMENT ON COLUMN @ANA@.dim_beneficiario.atualizado_em IS 'Última vez em que a linha foi gravada ou alterada.';

COMMENT ON TABLE @ANA@.dim_perfil_viagem IS 'Dimensão de perfil da viagem: combinação de situação, tipo e urgência.';
COMMENT ON COLUMN @ANA@.dim_perfil_viagem.perfil_key IS 'Chave da dimensão, derivada das três colunas de perfil.';
COMMENT ON COLUMN @ANA@.dim_perfil_viagem.situacao IS 'Realizada ou Não realizada (viagem cancelada continua aparecendo).';
COMMENT ON COLUMN @ANA@.dim_perfil_viagem.tipo_viagem IS 'Nacional ou Internacional.';
COMMENT ON COLUMN @ANA@.dim_perfil_viagem.urgencia_viagem IS 'Sim, Não ou Sigiloso (só existe a partir de 2020).';
COMMENT ON COLUMN @ANA@.dim_perfil_viagem.atualizado_em IS 'Última vez em que a linha foi gravada ou alterada.';

COMMENT ON TABLE @ANA@.fct_viagem IS 'Fato de viagem: uma linha por viagem, com as chaves das dimensões e os valores em R$.';
COMMENT ON COLUMN @ANA@.fct_viagem.pcdp IS 'Número da proposta de concessão de diárias e passagens (único; só existe a partir de 2020).';
COMMENT ON COLUMN @ANA@.fct_viagem.num_pcdp IS 'PCDP no formato número/ano (ex.: 001736/26); pode ter complemento (-1C) ou o texto de sigilo.';
COMMENT ON COLUMN @ANA@.fct_viagem.dias_afastamento IS 'Derivado: dias entre início e fim, contando os dois extremos.';
COMMENT ON COLUMN @ANA@.fct_viagem.atualizado_em IS 'Última vez em que a linha foi gravada ou alterada.';
COMMENT ON COLUMN @ANA@.fct_viagem.valor_total_viagem IS 'Valor total da viagem (R$): diárias + passagem + taxa + restituição + outros gastos.';
COMMENT ON COLUMN @ANA@.fct_viagem.valor_passagem IS 'Valor das passagens (R$).';
COMMENT ON COLUMN @ANA@.fct_viagem.valor_diarias IS 'Valor das diárias (R$).';
COMMENT ON COLUMN @ANA@.fct_viagem.valor_taxa_agenciamento IS 'Taxa de agenciamento (R$); zero no MPS.';
COMMENT ON COLUMN @ANA@.fct_viagem.valor_restituicao IS 'Restituição (R$); entra somada no total.';
COMMENT ON COLUMN @ANA@.fct_viagem.valor_devolucao IS 'Devolução (R$); não entra no total.';
COMMENT ON COLUMN @ANA@.fct_viagem.valor_multa IS 'Multa (R$); zero em todas as viagens observadas.';
COMMENT ON COLUMN @ANA@.fct_viagem.valor_outros_gastos IS 'Outros gastos (R$): total menos passagem, diárias, taxa e restituição. A API não expõe esse campo.';
COMMENT ON COLUMN @ANA@.fct_viagem.viagem_id IS 'Id da viagem na API; chave do fato.';
COMMENT ON COLUMN @ANA@.fct_viagem.data_inicio_key IS 'Chave para dim_data: início do afastamento.';
COMMENT ON COLUMN @ANA@.fct_viagem.data_fim_key IS 'Chave para dim_data: fim do afastamento.';
COMMENT ON COLUMN @ANA@.fct_viagem.orgao_siafi IS 'Chave para dim_orgao (código SIAFI do órgão solicitante).';
COMMENT ON COLUMN @ANA@.fct_viagem.ug_codigo IS 'Chave para dim_ug.';
COMMENT ON COLUMN @ANA@.fct_viagem.beneficiario_key IS 'Chave para dim_beneficiario.';
COMMENT ON COLUMN @ANA@.fct_viagem.perfil_key IS 'Chave para dim_perfil_viagem.';

COMMENT ON TABLE @ANA@.obt_viagem IS 'One big table: fato com as dimensões já desnormalizadas, pronta para o painel.';
COMMENT ON COLUMN @ANA@.obt_viagem.pcdp IS 'Número da proposta de concessão de diárias e passagens (único; só existe a partir de 2020).';
COMMENT ON COLUMN @ANA@.obt_viagem.num_pcdp IS 'PCDP no formato número/ano (ex.: 001736/26); pode ter complemento (-1C) ou o texto de sigilo.';
COMMENT ON COLUMN @ANA@.obt_viagem.situacao IS 'Realizada ou Não realizada (viagem cancelada continua aparecendo).';
COMMENT ON COLUMN @ANA@.obt_viagem.tipo_viagem IS 'Nacional ou Internacional.';
COMMENT ON COLUMN @ANA@.obt_viagem.urgencia_viagem IS 'Sim, Não ou Sigiloso (só existe a partir de 2020).';
COMMENT ON COLUMN @ANA@.obt_viagem.beneficiario_nome IS 'Nome do viajante; "Informações protegidas por sigilo" nas viagens sigilosas.';
COMMENT ON COLUMN @ANA@.obt_viagem.cpf_mascarado IS 'CPF como a API entrega, mascarado (***.947.711-**). Não serve de chave de pesquisa.';
COMMENT ON COLUMN @ANA@.obt_viagem.orgao_siafi IS 'Código SIAFI (5 dígitos) do órgão solicitante; é o filtro codigoOrgao da API.';
COMMENT ON COLUMN @ANA@.obt_viagem.orgao_nome IS 'Nome do órgão solicitante.';
COMMENT ON COLUMN @ANA@.obt_viagem.orgao_sigla IS 'Sigla do órgão solicitante.';
COMMENT ON COLUMN @ANA@.obt_viagem.orgao_maximo_sigla IS 'Sigla do órgão superior (ministério).';
COMMENT ON COLUMN @ANA@.obt_viagem.ug_codigo IS 'Código da unidade gestora responsável; -1 e -11 são códigos sem UG real.';
COMMENT ON COLUMN @ANA@.obt_viagem.ug_nome IS 'Nome da unidade gestora responsável.';
COMMENT ON COLUMN @ANA@.obt_viagem.dias_afastamento IS 'Derivado: dias entre início e fim, contando os dois extremos.';
COMMENT ON COLUMN @ANA@.obt_viagem.atualizado_em IS 'Última vez em que a linha foi gravada ou alterada.';
COMMENT ON COLUMN @ANA@.obt_viagem.valor_total_viagem IS 'Valor total da viagem (R$): diárias + passagem + taxa + restituição + outros gastos.';
COMMENT ON COLUMN @ANA@.obt_viagem.valor_passagem IS 'Valor das passagens (R$).';
COMMENT ON COLUMN @ANA@.obt_viagem.valor_diarias IS 'Valor das diárias (R$).';
COMMENT ON COLUMN @ANA@.obt_viagem.valor_taxa_agenciamento IS 'Taxa de agenciamento (R$); zero no MPS.';
COMMENT ON COLUMN @ANA@.obt_viagem.valor_restituicao IS 'Restituição (R$); entra somada no total.';
COMMENT ON COLUMN @ANA@.obt_viagem.valor_devolucao IS 'Devolução (R$); não entra no total.';
COMMENT ON COLUMN @ANA@.obt_viagem.valor_multa IS 'Multa (R$); zero em todas as viagens observadas.';
COMMENT ON COLUMN @ANA@.obt_viagem.valor_outros_gastos IS 'Outros gastos (R$): total menos passagem, diárias, taxa e restituição. A API não expõe esse campo.';
COMMENT ON COLUMN @ANA@.obt_viagem.viagem_id IS 'Id da viagem na API.';
COMMENT ON COLUMN @ANA@.obt_viagem.data_inicio IS 'Início do afastamento.';
COMMENT ON COLUMN @ANA@.obt_viagem.data_fim IS 'Fim do afastamento.';
COMMENT ON COLUMN @ANA@.obt_viagem.ano_inicio IS 'Ano do início.';
COMMENT ON COLUMN @ANA@.obt_viagem.mes_inicio IS 'Mês do início (1 a 12).';
COMMENT ON COLUMN @ANA@.obt_viagem.ano_mes_inicio IS 'Ano e mês do início (YYYY-MM).';
COMMENT ON COLUMN @ANA@.obt_viagem.trimestre_inicio IS 'Trimestre do início (1 a 4).';

COMMENT ON VIEW @STG@.vw_ctl_pendencias IS 'Janelas que não estão OK ou em que a quantidade da API difere da carregada.';
COMMENT ON VIEW @STG@.vw_ctl_tardios IS 'Viagens antigas (início há mais de 3 meses) que o portal publicou com atraso nos últimos 2 dias.';
COMMENT ON VIEW @STG@.vw_ctl_erros_abertos IS 'Erros ainda abertos, com as horas desde a primeira ocorrência (horas_aberto).';
COMMENT ON VIEW @STG@.vw_ctl_execucoes IS 'Execuções da carga com a duração em minutos.';
COMMENT ON VIEW @STG@.vw_ctl_saude IS 'Resumo de saúde da carga: janelas, erros, registros da API contra carregados, última execução e marca da analítica.';

COMMENT ON COLUMN @STG@.vw_ctl_pendencias.orgao IS 'Código SIAFI consultado.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.ida_mes IS 'Primeiro dia do mês de ida da janela.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.retorno_mes IS 'Primeiro dia do mês de retorno da janela.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.status IS 'OK quando a janela foi lida e conferida; qualquer outro valor é pendência.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.paginas_lidas IS 'Páginas lidas na API até vir a página vazia.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.qtd_api IS 'Registros devolvidos pela API na janela.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.qtd_carregada IS 'Registros da janela presentes na staging após a carga; deve ser igual a qtd_api.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.qtd_novos IS 'Viagens novas na staging nesta leitura.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.qtd_alterados IS 'Viagens que já existiam e mudaram (hash diferente) nesta leitura.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.tentativas IS 'Quantas vezes a janela foi tentada.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.aviso IS 'Observação que não impede a carga.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.erro IS 'Mensagem do último erro da janela.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.inicio IS 'Início da última leitura da janela.';
COMMENT ON COLUMN @STG@.vw_ctl_pendencias.fim IS 'Fim da última leitura da janela.';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.horas_aberto IS 'Horas desde a primeira ocorrência do erro.';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.chave IS 'Identificador do erro: janela mais etapa.';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.orgao IS 'Código SIAFI da janela com erro.';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.ida_mes IS 'Mês de ida da janela com erro.';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.retorno_mes IS 'Mês de retorno da janela com erro.';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.etapa IS 'Etapa em que falhou (extração, staging, intermediária ou analítica).';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.codigo IS 'Código do erro (HTTP ou interno).';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.mensagem IS 'Mensagem do erro, sem dados sensíveis.';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.tentativas IS 'Quantas vezes o erro se repetiu.';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.primeira_ocorrencia IS 'Quando o erro apareceu pela primeira vez.';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.ultima_ocorrencia IS 'Última vez em que o erro se repetiu.';
COMMENT ON COLUMN @STG@.vw_ctl_erros_abertos.execucao_id IS 'Execução (ctl_execucao.id) em que ocorreu por último.';
COMMENT ON COLUMN @STG@.vw_ctl_execucoes.minutos IS 'Duração da execução em minutos (até agora, se ainda roda).';
COMMENT ON COLUMN @STG@.vw_ctl_execucoes.id IS 'Número da execução.';
COMMENT ON COLUMN @STG@.vw_ctl_execucoes.modo IS 'Modo da execução (diario, completo ou reconstruir-silver).';
COMMENT ON COLUMN @STG@.vw_ctl_execucoes.status IS 'Situação da execução (em execução, concluída, com erros ou interrompida).';
COMMENT ON COLUMN @STG@.vw_ctl_execucoes.inicio IS 'Início da execução.';
COMMENT ON COLUMN @STG@.vw_ctl_execucoes.fim IS 'Fim da execução; nulo enquanto roda ou se foi interrompida.';
COMMENT ON COLUMN @STG@.vw_ctl_execucoes.janelas_total IS 'Janelas planejadas para a execução.';
COMMENT ON COLUMN @STG@.vw_ctl_execucoes.janelas_lidas IS 'Janelas lidas com sucesso.';
COMMENT ON COLUMN @STG@.vw_ctl_execucoes.janelas_erro IS 'Janelas que terminaram com erro.';
COMMENT ON COLUMN @STG@.vw_ctl_execucoes.novos IS 'Viagens novas gravadas na staging.';
COMMENT ON COLUMN @STG@.vw_ctl_execucoes.alterados IS 'Viagens alteradas na staging.';
COMMENT ON COLUMN @STG@.vw_ctl_tardios.carregado_em IS 'Quando a viagem entrou na staging.';
COMMENT ON COLUMN @STG@.vw_ctl_tardios.id IS 'Id da viagem na API.';
COMMENT ON COLUMN @STG@.vw_ctl_tardios.data_inicio IS 'Início do afastamento (dataInicioAfastamento).';
COMMENT ON COLUMN @STG@.vw_ctl_tardios.data_fim IS 'Fim do afastamento (dataFimAfastamento); sempre maior ou igual ao início.';
COMMENT ON COLUMN @STG@.vw_ctl_tardios.janela_ida IS 'Primeiro dia do mês de ida da janela em que a viagem foi lida.';
COMMENT ON COLUMN @STG@.vw_ctl_tardios.janela_retorno IS 'Primeiro dia do mês de retorno da janela em que a viagem foi lida.';
COMMENT ON COLUMN @STG@.vw_ctl_saude.janelas_total IS 'Janelas conhecidas em ctl_janela.';
COMMENT ON COLUMN @STG@.vw_ctl_saude.janelas_ok IS 'Janelas com status OK.';
COMMENT ON COLUMN @STG@.vw_ctl_saude.janelas_pendentes IS 'Janelas com status diferente de OK.';
COMMENT ON COLUMN @STG@.vw_ctl_saude.erros_abertos IS 'Erros ainda abertos em ctl_erro.';
COMMENT ON COLUMN @STG@.vw_ctl_saude.erros_resolvidos IS 'Erros já corrigidos (ctl_erro_historico).';
COMMENT ON COLUMN @STG@.vw_ctl_saude.registros_api IS 'Soma dos registros que a API devolveu em todas as janelas.';
COMMENT ON COLUMN @STG@.vw_ctl_saude.registros_carregados IS 'Soma dos registros carregados na staging; deve igualar registros_api.';
COMMENT ON COLUMN @STG@.vw_ctl_saude.ultima_execucao_status IS 'Status da última execução.';
COMMENT ON COLUMN @STG@.vw_ctl_saude.ultima_execucao_fim IS 'Fim da última execução.';
COMMENT ON COLUMN @STG@.vw_ctl_saude.ultima_execucao_concluida IS 'Fim da última execução concluída com sucesso.';
COMMENT ON COLUMN @STG@.vw_ctl_saude.marca_analitica IS 'Marca d''água da camada analítica (ctl_camada).';
