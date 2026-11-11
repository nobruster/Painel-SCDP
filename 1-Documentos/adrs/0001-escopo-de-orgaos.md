# ADR 0001: escopo de órgãos da carga

Status: Proposto (aguarda decisão do dono do projeto)

Data: 2026-11-11. Decisão 5.1 do PRD; bloqueia a carga final.

## Contexto

- `codigoOrgao` da API filtra pela **entidade**, não pelo órgão superior. Consultar `33000` não traz as entidades vinculadas.
- O órgão máximo MPS (`orgaoMaximo.sigla = MPS`) reúne três entidades com viagens. Em ago/2026:

| Entidade | SIAFI | Viagens em ago/2026 |
|---|---|---|
| Ministério da Previdência Social (MPS) | `33000` | 142 |
| INSS | `37202` | 1.265 |
| PREVIC | `33206` | 22 |

- Hoje o `.env` usa só `33000`: 3.411 viagens carregadas (1.951 de 2025 + 1.460 de 2026), validadas contra o download oficial.
- O INSS tem cerca de nove vezes o volume do `33000` (1.265 contra 142 em ago/2026).
- O código já aceita lista em `CODIGO_ORGAO` (valores SIAFI de 5 dígitos separados por vírgula, `scdp.config.parse_orgaos`); mudar o escopo é configuração, não código.
- A janela de busca é mês de ida × mês de retorno (0 a +12 meses): 312 janelas em out/2026 e 325 em nov/2026, e cada órgão percorre todas.
- Limite do Portal: 400 req/min das 6:00 às 23:59 e 700 req/min das 0:00 às 5:59. O projeto usa 50% (`USO_DO_LIMITE`): 200 e 350 req/min.

## Opções

1. **Só `33000`.** Mantém o que existe.
2. **`33000` + INSS (`37202`) + PREVIC (`33206`).** As três entidades conhecidas do MPS, configuradas à mão.
3. **Todo o MPS descoberto por `orgaoMaximo`.** A lista de entidades sai da própria API, sem lista fixa.

## Recomendação

Opção 2, em duas etapas: primeiro `33000` + `33206` (volume pequeno, valida o multiórgão em produção) e depois `37202` depois de medir o tempo da carga completa. Justificativa: o painel de "viagens do MPS" fica incompleto sem o INSS (cerca de 89% das viagens do ministério em ago/2026), a lista fixa é conferível e não exige código novo, e a descoberta automática (opção 3) só se justifica se aparecerem entidades novas. A decisão final é do dono do projeto.

## Decisão

Pendente. Este ADR permanece como Proposto até a aprovação do dono do projeto.

## Alternativas rejeitadas

- **Só `33000` como definitivo:** rejeitada como recomendação, não como possibilidade. É a mais barata e já validada, mas deixa o INSS e a PREVIC de fora e o painel não representa o ministério. Segue válida se o escopo do painel for só a administração central.
- **Descoberta automática por `orgaoMaximo` (opção 3):** rejeitada por ora. Exigiria código novo para listar entidades, e uma entidade nova entraria na carga sem revisão de volume e de custo. Reavaliar se a lista de vinculadas mudar com frequência.

## Consequencias

- **Volume:** com o INSS, a base cresce em ordem de grandeza (ago/2026: 142 viagens em `33000` contra 1.265 no INSS). Staging, intermediária e analítica ficam maiores; o `obt_viagem` precisa ser reavaliado para o painel.
- **Rate limit e tempo:** cada órgão repete as 312/325 janelas (cresce 13 por mês). O INSS sozinho tem 85 páginas em ago/2026 (1.265 / 15 por página). A 200 req/min (dia) ou 350 req/min (madrugada), o custo da carga completa sobe de forma proporcional ao número de páginas, e a completa roda às 03:30, na faixa de 700 req/min. O tempo real deve ser medido antes de ativar o INSS; o timeout das DAGs pode precisar de ajuste.
- **Carga diária:** lê as janelas com ida ou retorno nos últimos 3 meses mais as pendentes (156); com três órgãos, o número de requisições da diária também multiplica.
- **Dimensão de órgão:** `dim_orgao` e os KPIs por órgão passam a ter mais de um valor; as views e o painel devem filtrar por entidade.
- **Configuração:** basta `CODIGO_ORGAO=33000,33206,37202` no `.env` do servidor. Incluir órgãos novos exige uma carga completa para eles (`--modo completo`).
- **Reversão:** voltar para `33000` não apaga os dados já carregados dos outros órgãos; seria preciso removê-los à parte.
