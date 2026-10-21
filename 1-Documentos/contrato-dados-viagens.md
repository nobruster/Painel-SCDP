# Contrato de dados: viagens a serviço (Portal da Transparência)

Verificado em 20/10/2026 com os downloads oficiais de 2025 (`2025_20260920_Viagens.zip`, 149 MB) e de 2026 (`2026_20260920_Viagens.zip`, 86 MB), ambos gerados em 20/09/2026, e com a API. O portal não publica um contrato formal (nenhum arquivo de layout no ZIP; o dicionário é uma página HTML sem tipos). Este documento é o contrato que **nós** adotamos, derivado dessas fontes e dos dados.

## 1. Como obter o arquivo
- Endereço: `https://portaldatransparencia.gov.br/download-de-dados/viagens/{ano}` responde 302 para `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/viagens/{ano}_{AAAAMMDD}_Viagens.zip` (a data no nome é a da geração do arquivo; o endereço sem data dá 403).
- Anos disponíveis: 2011 a 2027. Chamada automatizada com `curl` funciona, desde que envie um `User-Agent` de navegador (sem ele, as páginas do portal respondem 405).
- O ZIP de 2025 tem 4 CSVs e nenhum outro arquivo: `2025_Viagem.csv` (496 MB), `2025_Trecho.csv` (292 MB), `2025_Pagamento.csv` (264 MB) e `2025_Passagem.csv` (105 MB).

## 2. Formato dos CSVs
| Item | Valor |
|---|---|
| Codificação | ISO-8859-1 (latin-1): a leitura como UTF-8 falha. Sem BOM |
| Separador / aspas | `;` e `"` em todos os campos |
| Decimal | vírgula (`1272,97`); sem separador de milhar |
| Datas | `dd/MM/aaaa`; horas `HH:mm` |
| Ausência | texto `Sem informação` em muitos campos; `""` em outros |
| Sim/Não | `SIM` / `NÃO` (Viagem Urgente), `Sim` / `Não` (Missão) |
| Identificador | 19 dígitos com zeros à esquerda, texto (`0000000000020150776`); igual ao `viagem.pcdp` da API |
| CPF | mascarado (`***.566.948-**`), como na API |

## 3. Colunas (nomes exatamente como vêm)
**Viagem (22):** Identificador do processo de viagem · Número da Proposta (PCDP) · Situação · Viagem Urgente · Justificativa Urgência Viagem · Código do órgão superior · Nome do órgão superior · Código órgão solicitante · Nome órgão solicitante · CPF viajante · Nome · Cargo · Função · Descrição Função · Período - Data de início · Período - Data de fim · Destinos · Motivo · Valor diárias · Valor passagens · Valor devolução · Valor outros gastos.

**Pagamento (10):** Identificador do processo de viagem · Número da Proposta (PCDP) · Código do órgão superior · Nome do órgão superior · Codigo do órgão pagador · Nome do órgao pagador · Código da unidade gestora pagadora · Nome da unidade gestora pagadora · Tipo de pagamento · Valor.

**Passagem (19):** Identificador do processo de viagem · Número da Proposta (PCDP) · Meio de transporte · País - Origem ida · UF - Origem ida · Cidade - Origem ida · País - Destino ida · UF - Destino ida · Cidade - Destino ida · País - Origem volta · UF - Origem volta · Cidade - Origem volta · Pais - Destino volta · UF - Destino volta · Cidade - Destino volta · Valor da passagem · Taxa de serviço · Data da emissão/compra · Hora da emissão/compra.

**Trecho (14):** Identificador do processo de viagem (com espaço no fim) · Número da Proposta (PCDP) · Sequência Trecho · Origem - Data · Origem - País · Origem - UF · Origem - Cidade · Destino - Data · Destino - País · Destino - UF · Destino - Cidade · Meio de transporte · Número Diárias · Missao?

## 4. Diferenças em relação ao dicionário HTML
- O arquivo tem colunas que o dicionário não lista: Número da Proposta (PCDP), Viagem Urgente, Justificativa Urgência Viagem, Função, Descrição Função, Valor devolução, Código da unidade gestora pagadora, Data e Hora da emissão/compra.
- O nome de várias colunas é inconsistente entre os arquivos (acento e espaço): `Codigo` × `Código`, `órgao` × `órgão`, `Pais` × `País`, `Missao?`, espaço no fim em `Identificador do processo de viagem ` no arquivo Trecho. **Não depender do texto do cabeçalho**: ler por posição ou normalizar (minúsculas, sem acento, sem espaços nas pontas).
- O dicionário chama a coluna de Pagamento de "Valor da Despesa" e de Passagem de "Valor da passagem"; o arquivo usa "Valor".

## 5. Correspondência com a API (`/viagens`)
| CSV (arquivo Viagem) | API | Confirmado |
|---|---|---|
| Identificador do processo de viagem | `viagem.pcdp` | formato igual (19 dígitos) |
| Número da Proposta (PCDP) | `viagem.numPcdp` | formato igual (`060767/25`, às vezes com complemento `-1C`; viagens sigilosas: ver seção 8) |
| Código órgão solicitante | `orgao.codigoSIAFI`, filtro `codigoOrgao` | sim: o MPS (`33000`) tem 1.951 viagens em 2025 nos dois lados |
| Código do órgão superior | `orgao.orgaoMaximo.codigo` | no MPS, superior `33000` reúne INSS (15.899), o próprio MPS (1.951) e PREVIC (214) em 2025 |
| Valor diárias + Valor passagens + Valor outros gastos | `valorTotalViagem` | **sim, em 12 de 12 meses de 2025 (MPS)** |
| Valor devolução | `valorTotalDevolucao` | fora do total, nos dois lados |
| Período - Data de início / fim | `dataInicioAfastamento` / `dataFimAfastamento` | sim |
| Situação, Viagem Urgente, Justificativa | `situacao`, `viagem.urgenciaViagem`, `viagem.justificativaUrgente` | nomes diferentes, mesmo conteúdo |

Consequência: o `valorTotalViagem` da API **é** diárias + passagens + outros gastos do arquivo. As colunas de taxa de agenciamento e de restituição da API estão dentro do valor de passagens do arquivo. Isso explica por que a soma dos componentes da API às vezes ficava abaixo do total (o resto era "outros gastos").

## 6. Conciliação executada (MPS, órgão solicitante `33000`, início em 2025)
| | Arquivo (CSV) | API carregada | Resultado |
|---|---|---|---|
| Viagens, mês a mês (jan a dez) | 31, 81, 118, 117, 87, 137, 96, 202, 538, 211, 220, 113 | idênticos | 12 de 12 meses iguais; total 1.951 |
| Valor, mês a mês | soma de diárias + passagens + outros | `valorTotalViagem` | 12 de 12 meses iguais; total R$ 11.534.624,24 |

O pico de 538 viagens em setembro de 2025 existe também no arquivo oficial, então é dado real e não erro de carga.

## 7. Pontos de atenção do arquivo
- **Ids repetidos:** o arquivo Viagem de 2025 tem 814.395 linhas e 814.392 ids únicos (3 repetidos, em outros órgãos). A carga deve tratar repetição, como já faz com a API.
- **Definição de "ano":** todas as 814.395 viagens do arquivo de 2025 têm início em 2025.
- **Atualização:** o arquivo é regerado (a data vai no nome). A periodicidade exata não foi confirmada.
- **Tamanho:** o arquivo Viagem tem 496 MB e cerca de 814 mil linhas por ano (todos os órgãos), então precisa ler em fluxo.
- **Dado pessoal:** nome e motivo vêm no arquivo, como na API; o CPF vem mascarado.

## 8. Validação do banco contra o contrato: 2025 (20/10/2026)
**Resultado: o que está carregado no banco está correto.** As poucas diferenças em relação ao arquivo oficial vêm das duas fontes oficiais se contradizerem, não de erro da carga.

**Comparação campo a campo, MPS (`33000`), início em 2025: 1.951 viagens no arquivo e 1.951 no banco, os mesmos ids nos dois lados (0 só de um lado).** 1.696 viagens são iguais em todos os campos. Nas 255 restantes:

| Campo | Viagens | Causa | Quem está "certo" |
|---|---|---|---|
| `motivo` | 107 | difere só em acento, pontuação ou espaço (o conteúdo alfanumérico é igual), efeito da conversão do texto para latin-1 no arquivo | sem diferença de conteúdo |
| `valor_outros_gastos` | 78 | em 78 viagens o arquivo põe a taxa de agenciamento e a restituição em "outros gastos"; nas outras 1.873 ele as põe em "passagens". O `valorTotalViagem` bate em todas | diferença de critério na própria fonte; o total não muda |
| `cpf_mascarado` | 72 | em 50 viagens o arquivo traz o CPF vazio e a API traz mascarado; em 22 viagens sigilosas o arquivo traz o CPF mascarado e a API vem vazia | as fontes discordam; o banco segue a API |
| `numPcdp` e urgência | 22 | viagens sigilosas: a API devolve `Informações protegidas por sigilo` e urgência `Sigiloso`; o arquivo traz o texto cortado em 13 caracteres e urgência `NÃO` | as fontes discordam; o banco segue a API |

Campos iguais em 100% das 1.951 viagens: situação, órgão superior e solicitante, nome, datas de início e fim, valor das diárias, valor da devolução e valor total.

**Regras do contrato aplicadas ao banco inteiro (3.411 viagens): todas passam.**
- id de processo com 19 dígitos; órgão SIAFI com 5 dígitos; situação, tipo de viagem e urgência dentro dos valores conhecidos;
- CPF no padrão mascarado; fim da viagem não anterior ao início; sem data ou valor total nulo; sem valor negativo; sem id repetido;
- valor total = diárias + passagem + taxa + restituição + outros gastos;
- as 4 camadas têm 3.411 viagens e nenhuma viagem da staging está sem linha na intermediária.

**Correção do contrato:** o número da proposta (`numPcdp`) tem três formatos: `000000/AA` (2.960 viagens), `000000/AA-1C` com complemento (407: `-1C`, `-2C`, `-3C`, `-4C`, `-6C`) e o texto `Informações protegidas por sigilo` (44, as viagens sigilosas). O ano do número é coerente com o ano de início (tolerância de 1 ano) em todas.

Não validado: as tabelas Passagem, Trecho e Pagamento, que o banco não carrega. Para 2026, ver a seção 9.

## 9. Contrato de 2026 (arquivo `2026_20260920_Viagens.zip`, 86 MB, gerado em 20/09/2026)
Mesmo método usado em 2025: baixar o arquivo oficial, comparar o layout e conferir o banco contra ele.

**Layout: idêntico ao de 2025.** Os 4 arquivos (`2026_Viagem.csv` 294 MB, `2026_Trecho.csv` 160 MB, `2026_Pagamento.csv` 147 MB, `2026_Passagem.csv` 64 MB) têm exatamente o mesmo cabeçalho de 2025: Viagem 22 colunas, Pagamento 10, Passagem 19 e Trecho 14. Mesma codificação (latin-1), separador, decimal e formato de data. **Isso reforça o contrato: o layout é estável entre os anos.**

**Arquivo:** 461.977 linhas com 461.977 ids únicos (nenhum repetido; em 2025 havia 3) e todas as viagens com início em 2026. O órgão solicitante `33000` tem 1.460 viagens.

**Banco contra o arquivo (MPS, início em 2026): os mesmos 1.460 ids nos dois lados (0 só de um lado).**

| Mês | Viagens (arquivo = banco) | Valor (arquivo = banco) |
|---|---|---|
| jan | 90 | R$ 472.311,49 |
| fev | 183 | R$ 1.145.493,71 |
| mar | 333 | R$ 2.018.898,84 |
| abr | 164 | R$ 928.038,47 |
| mai | 224 | R$ 1.100.331,28 |
| jun | 202 | R$ 1.343.913,80 |
| jul | 113 | R$ 646.156,29 |
| ago | 145 | R$ 556.945,17 |
| set | 6 | R$ 21.045,18 |

**9 de 9 meses iguais em quantidade e em valor.** Comparação campo a campo: 1.236 das 1.460 viagens são idênticas em todos os campos; as 224 restantes são as mesmas diferenças entre fontes de 2025:

| Campo | Viagens | Causa |
|---|---|---|
| `cpf_mascarado` | 146 | em 124 viagens o arquivo traz o CPF vazio e a API traz mascarado (em 37 delas o cargo também vem vazio no arquivo); em 22 viagens sigilosas o arquivo traz o CPF mascarado e a API vem vazia |
| `valor_outros_gastos` | 87 | o arquivo põe taxa de agenciamento e restituição em "outros gastos" em 87 viagens e em "passagens" nas outras 1.373; o total bate em todas |
| `numPcdp` e urgência | 22 | viagens sigilosas (a API traz o texto de sigilo e `Sigiloso`; o arquivo traz o texto cortado e `NÃO`) |

As 12 regras do contrato (formato do id e do `numPcdp`, valores possíveis, CPF mascarado, datas, valores, total e ausência de repetição) passam no banco inteiro.

**Resumo dos dois anos (MPS, órgão `33000`)**

| | 2025 | 2026 |
|---|---|---|
| Viagens no arquivo = no banco | 1.951 | 1.460 |
| Meses iguais em quantidade e valor | 12 de 12 | 9 de 9 |
| Viagens idênticas em todos os campos | 1.696 | 1.236 |
| Divergências | só entre as duas fontes oficiais | só entre as duas fontes oficiais |
| Layout do arquivo | referência | idêntico |

O arquivo de 2026 foi gerado em 20/09/2026, então traz viagens até setembro (6 em setembro, como o banco). Viagens de outubro só aparecem no próximo arquivo.

## 10. Como este contrato vira teste
1. **Layout da API:** comparar o conjunto de chaves do JSON da API com o esperado antes de gravar (hoje a carga não faz isso).
2. **Conciliação independente:** por ano, contar no arquivo de download as viagens por órgão solicitante e mês e comparar com o carregado pela API (o que foi feito à mão na seção 6).
3. **Layout do arquivo:** conferir número e ordem das colunas de cada CSV, mais codificação e separador.
