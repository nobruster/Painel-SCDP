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
    alterados      int
);

CREATE OR REPLACE VIEW @STG@.vw_ctl_pendencias AS
SELECT * FROM @STG@.ctl_janela WHERE status <> 'OK' OR qtd_api IS DISTINCT FROM qtd_carregada;

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
INSERT INTO @ANA@.dim_data
SELECT d::date, extract(year FROM d)::int, extract(quarter FROM d)::int, extract(month FROM d)::int,
       to_char(d, 'YYYY-MM'), extract(isodow FROM d)::int, extract(isodow FROM d) IN (6, 7)
FROM generate_series('2020-01-01'::date, '2030-12-31'::date, interval '1 day') AS d
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
