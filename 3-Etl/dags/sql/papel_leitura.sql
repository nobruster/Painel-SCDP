-- Papel somente leitura do painel. Aplicado a parte do schema.sql (nao entra no hash do schema): rodar apos a carga criar as camadas.
-- Reaplicavel a qualquer momento (para cobrir objetos novos); a senha/LOGIN fica fora do arquivo (ALTER ROLE ... LOGIN PASSWORD no cofre).
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'scdp_leitura') THEN
        CREATE ROLE scdp_leitura NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;
    END IF;
END $$;

GRANT USAGE ON SCHEMA @ANA@ TO scdp_leitura;
GRANT SELECT ON ALL TABLES IN SCHEMA @ANA@ TO scdp_leitura;

GRANT USAGE ON SCHEMA @STG@ TO scdp_leitura;
REVOKE ALL ON ALL TABLES IN SCHEMA @STG@ FROM scdp_leitura;
DO $$
DECLARE v record;
BEGIN
    FOR v IN SELECT schemaname, viewname FROM pg_views
             WHERE schemaname = '@STG@' AND viewname LIKE 'vw\_ctl\_%'
    LOOP
        EXECUTE format('GRANT SELECT ON %I.%I TO scdp_leitura', v.schemaname, v.viewname);
    END LOOP;
END $$;

REVOKE ALL ON SCHEMA @INT@ FROM scdp_leitura;
REVOKE ALL ON ALL TABLES IN SCHEMA @INT@ FROM scdp_leitura;
