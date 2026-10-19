# Dicionário de dados: Viagens a Serviço (Portal da Transparência)

Fonte: https://portaldatransparencia.gov.br/dicionario-de-dados/viagens (título da página: "Dicionário de Dados – Viagens a Serviço – Pagamentos").
Copiado em 19/10/2026. A página não oferece arquivo para baixar (sem PDF, planilha ou CSV); o conteúdo abaixo é a transcrição das 4 tabelas.
Descreve os 4 arquivos do download em lote (`/download-de-dados/viagens`: Pagamento, Passagem, Trecho e Viagem). **Não é o dicionário da API**: a API tem estrutura própria (ver `referencia_api.md`).

## Arquivo Viagem
| Coluna | Descrição |
|---|---|
| Identificador do processo de viagem | Número que identifica o processo de concessão da viagem |
| Situação | Situação da viagem: "não realizada"; "realizada" |
| Código do Órgão Superior | Código do Órgão Superior que custeou despesas da viagem. Órgão superior: unidade da Administração Direta que tenha entidades por ele supervisionadas (Manual do SIAFI) |
| Nome Órgão Superior | Nome do Órgão Superior |
| Código Solicitante | Código do Órgão que solicitou a viagem. Órgão subordinado: entidade supervisionada por um órgão da Administração Direta (Manual do SIAFI) |
| Nome Órgão Solicitante | Nome do Órgão |
| CPF viajante | CPF da pessoa que realizou a viagem |
| Nome | Nome do viajante |
| Cargo | Cargo do viajante |
| Período - Data de início | Data de início de afastamento do servidor |
| Período - Data de fim | Data de fim de afastamento do servidor |
| Destinos | Locais pelos quais o viajante passará durante a viagem |
| Motivo | Motivo da viagem |
| Valor Diárias | Valor de diárias pagas pelo órgão, se houver |
| Valor Passagens | Valor de passagens pagas pelo órgão, se houver |
| Valor Outros Gastos | Valor de outros gastos pagos pelo órgão, se houver |

## Arquivo Pagamento
| Coluna | Descrição |
|---|---|
| Identificador do processo de viagem | Número que identifica o processo de concessão da viagem |
| Código do Órgão Superior | Código do Órgão Superior que custeou a despesa (Manual do SIAFI) |
| Nome Órgão Superior | Nome do Órgão Superior |
| Código Órgão Pagador | Código do Órgão que pagou a despesa. Órgão subordinado: entidade supervisionada por um órgão da Administração Direta (Manual do SIAFI) |
| Nome Órgão Pagador | Nome do Órgão |
| Código UG Pagadora | Código da Unidade Gestora que pagou a despesa. UG: unidade orçamentária ou administrativa que realiza atos de gestão orçamentária, financeira e/ou patrimonial, cujo titular está sujeito a tomada de contas anual (arts. 81 e 82 do Decreto-lei 200/1967; Manual do SIAFI) |
| Nome UG Pagadora | Nome da Unidade Gestora |
| Tipo de Pagamento | Tipo da despesa paga pelo órgão (diária, passagem, seguro, etc.) |
| Valor da Despesa | Valor da despesa paga |

## Arquivo Passagem
| Coluna | Descrição |
|---|---|
| Identificador do processo de viagem | Número que identifica o processo de concessão da viagem |
| Meio de transporte | Meio de transporte da passagem |
| País – Origem Ida / UF - Origem Ida / Cidade - Origem Ida | País, UF e cidade de origem na ida |
| País - Destino Ida / UF – Destino Ida / Cidade – Destino Ida | País, UF e cidade de destino na ida |
| País – Origem Volta / UF - Origem Volta / Cidade - Origem Volta | País, UF e cidade de origem na volta |
| País - Destino Volta / UF – Destino Volta / Cidade – Destino Volta | País, UF e cidade de destino na volta |
| Valor da passagem | Valor da passagem |
| Taxa de serviço | Taxa de serviço da passagem |

## Arquivo Trecho
| Coluna | Descrição |
|---|---|
| Identificador do processo de viagem | Número que identifica o processo de concessão da viagem |
| Sequência Trecho | Sequência do trecho na viagem |
| Origem - Data | Data de saída da origem |
| Origem – País / Origem – UF / Origem – Cidade | País, UF e cidade de origem |
| Destino - Data | Data de chegada no destino |
| Destino – País / Destino – UF / Destino – Cidade | País, UF e cidade de destino |
| Meio de transporte | Meio de transporte da origem para o destino |
| Número Diárias | Número de diárias do trecho |
| Missão? | Houve missão no trecho? "Sim" ou "Não" |

## Correspondência com a API (`/viagens`)
Feita por nome e por valores observados nos dados carregados. É interpretação nossa, **a confirmar com o dono da API** (perguntas 3.1, 4.1 e 4.2).

| Dicionário (arquivo Viagem) | Campo da API | Observação |
|---|---|---|
| Identificador do processo de viagem | `viagem.pcdp` | Mesmo formato (19 dígitos com zeros à esquerda) exibido na tela de consulta. O `id` da API é outro número |
| Situação | `situacao` | |
| Código / Nome Órgão Superior | `orgao.orgaoMaximo.codigo` / `.nome` | |
| Código / Nome Órgão Solicitante | `orgao.codigoSIAFI` / `orgao.nome` | `codigoOrgao` da consulta filtra este campo |
| CPF viajante | `beneficiario.cpfFormatado` | Vem mascarado na API |
| Nome | `beneficiario.nome` | "Informações protegidas por sigilo" em viagens sigilosas |
| Cargo | `cargo.descricao` | Vem vazio na maioria dos registros |
| Período - Data de início / fim | `dataInicioAfastamento` / `dataFimAfastamento` | |
| Motivo | `viagem.motivo` | |
| Valor Diárias | `valorTotalDiarias` | |
| Valor Passagens | `valorTotalPassagem` | |
| Valor Outros Gastos | **não existe** | Está incluído em `valorTotalViagem` (explica os 26 totais que não fecham) |
| Destinos | **não existe** | |

Só na API (não aparecem no dicionário): `id`, `viagem.numPcdp`, `viagem.ano`, `viagem.urgenciaViagem`, `viagem.justificativaUrgente`, `tipoViagem`, `funcao`, `beneficiario.nis`, `orgaoPagamento`, `unidadeGestoraResponsavel`, `valorTotalRestituicao`, `valorTotalTaxaAgenciamento`, `valorTotalDevolucao`, `valorMulta`, `valorTotalViagem`.
Arquivos Passagem, Trecho e Pagamento (origem/destino, meio de transporte, número de diárias, tipo de pagamento, UG pagadora) não têm equivalente na API.
