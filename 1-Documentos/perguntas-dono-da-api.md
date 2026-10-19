# Perguntas para o dono da API (Portal da Transparência, CGU)

Contato oficial (spec da API): Diretoria de Tecnologia da Informação (DTI), CGU, listaapitransparencia@cgu.gov.br.
Escopo: API de dados, grupo "Viagens a serviço" (`/viagens`, `/viagens/{id}`, `/viagens-por-cpf`) e download de dados abertos de viagens.
Resumo do projeto: carga incremental diária das viagens do MPS para um banco próprio, com conciliação por janela.

Prioridade: **A** = bloqueia o desenho; **B** = melhora a robustez; **C** = esclarecimento.

## 1. Completude e atraso dos dados
| # | Pergunta | Por que perguntamos | Prior. |
|---|---|---|---|
| 1.1 | Qual é a frequência de atualização da base da API de viagens e qual o atraso normal entre o registro no SCDP e a publicação? | A tela de consulta informa "dados atualizados até 04/09/2026" em 19/10/2026 (≈45 dias), mas a API devolve viagens com ida em outubro de outros órgãos | A |
| 1.2 | A API e o download em lote usam a mesma base e a mesma data de corte? | Queremos usar o download para o histórico e a API para o incremental | A |
| 1.3 | Viagens já publicadas podem ser alteradas ou corrigidas depois (valores, datas, situação, órgão)? Com que prazo máximo? | Precisamos definir por quanto tempo reler janelas antigas | A |
| 1.4 | Viagens podem ser removidas da base? Há registro dessas exclusões? | A carga não apaga registros; precisamos saber se isso gera divergência | A |
| 1.5 | Existe campo ou endpoint com data/hora de última atualização do registro, ou filtro por data de alteração? | Hoje só dá para detectar mudança relendo tudo e comparando hash | A |
| 1.6 | Viagens sem data de retorno (em andamento ou com dado faltando) são publicadas? Como acessá-las, já que as 4 datas são obrigatórias? | Registros sem retorno não caem em nenhuma janela de consulta | A |
| 1.7 | Por que os 4 parâmetros de data são obrigatórios e o intervalo máximo é de 1 mês? Há previsão de filtro por data de atualização ou por ano? | Exige 150+ consultas (mês de ida × mês de retorno) para cobrir um ano | B |

## 2. Escopo de órgãos
| # | Pergunta | Por que perguntamos | Prior. |
|---|---|---|---|
| 2.1 | `codigoOrgao` filtra a entidade, não o ministério (Marinha `52131` devolve viagens, Defesa `52000` quase nada). Existe forma de consultar por órgão superior/máximo, ou um endpoint com a hierarquia órgão superior → entidades vinculadas? | No MPS: `33000` = 142 viagens em ago/2026, INSS `37202` = 1.265, PREVIC `33206` = 22 | A |
| 2.2 | Qual é o código de órgão correto para o "MPS" e suas vinculadas? O código `308819` (informado internamente) não existe nas listas SIAFI nem SIAPE. Ele corresponde a algum identificador do SCDP (UG, unidade, código de órgão solicitante)? | A API devolve `[]` para esse código | A |
| 2.3 | A lista de `/orgaos-siafi` tem entradas "CODIGO INVALIDO". São órgãos extintos? Podem ter viagens históricas? | 766 órgãos na lista; vários sem nome | C |
| 2.4 | A busca por `descricao` em `/orgaos-siafi` e `/orgaos-siape` diferencia maiúsculas e acentos. É intencional? | `previdencia` devolve `[]`, `Previdência` funciona | C |

## 3. Campos e significado dos valores
| # | Pergunta | Por que perguntamos | Prior. |
|---|---|---|---|
| 3.1 | O dicionário de dados do download cita "Valor Outros Gastos", mas a API não tem esse campo. O `valorTotalViagem` inclui outros gastos? Podem expor o campo? | Em 26 de 1.460 viagens o total é maior que passagem + diárias + taxa + restituição | A |
| 3.2 | Qual é a fórmula oficial de `valorTotalViagem`? Como entram restituição, devolução, multa e taxa de agenciamento? | Restituição é somada ao total e devolução não; precisamos confirmar | A |
| 3.3 | Quais são os valores possíveis (domínio) de `situacao`, `tipoViagem` e `urgenciaViagem`? | Observamos "Realizada"/"Não realizada", "Nacional"/"Internacional" e "Sim"/"Não"/"Sigiloso" | B |
| 3.4 | O que significam as unidades gestoras `-1` ("Sem informação") e `-11` ("Sigilosa")? | Aparecem em 17 e 22 registros de 2026 | B |
| 3.5 | Viagens "Não realizada" mantêm valor de passagem e diárias. Esse valor foi pago, reservado ou cancelado? | Há viagens "Não realizada" com valor alto | B |
| 3.6 | `cargo.descricao` e `beneficiario.nis` vêm vazios na maioria dos registros. É esperado? | Campos presentes na estrutura, mas sem conteúdo | C |
| 3.7 | PCDP e "viagem urgente" só existem a partir de 2020 (tela de consulta). A API segue a mesma regra? | Para decidir o que tratar como ausente | C |

## 4. Passagens, trechos e pagamentos
| # | Pergunta | Por que perguntamos | Prior. |
|---|---|---|---|
| 4.1 | A API tem só 3 endpoints de viagens. Há previsão de endpoints de trecho, passagem e pagamento, que existem no download? | Só o download traz esses dados | A |
| 4.2 | O "Identificador do processo de viagem" dos 4 arquivos do download corresponde a `viagem.pcdp` da API (19 dígitos, igual ao da tela) ou ao `id`? Qual é a chave para ligar API e planilha? | Precisamos ligar API e planilha; ver `dicionario-de-dados-viagens.md` | A |

## 5. Identificação de pessoas e LGPD
| # | Pergunta | Por que perguntamos | Prior. |
|---|---|---|---|
| 5.1 | Existe um identificador estável e não reversível da pessoa (hash, id de pessoa) que permita agrupar viagens do mesmo viajante sem o CPF completo? | O CPF vem mascarado e há homônimos; `/viagens-por-cpf` exige CPF completo | A |
| 5.2 | Como o portal trata o campo `motivo` (texto livre) do ponto de vista de dados pessoais? Há mascaramento prévio? | Optamos por não levar `motivo` à camada de consumo | B |
| 5.3 | O que determina uma viagem "sigilosa" e há outros campos suprimidos além do nome? | Nome vem como "Informações protegidas por sigilo" | C |
| 5.4 | Quais orientações de LGPD valem para quem armazena nome + CPF parcial em base própria? | Definir retenção e acesso | B |

## 6. Limites, estabilidade e uso
| # | Pergunta | Por que perguntamos | Prior. |
|---|---|---|---|
| 6.1 | O limite de 400 req/min (6h–23h59) e 700 req/min (0h–5h59) vale por chave ou por IP? Existem limites menores por endpoint ("restritos")? | Texto oficial cita só 400/700 | A |
| 6.2 | Qual a penalidade por excesso (suspensão), por quanto tempo e como reativar? | Fonte de terceiros fala em 8 h | A |
| 6.3 | A API devolve cabeçalhos de limite (`Retry-After`, requisições restantes) no erro 429? | Para pausar com precisão | B |
| 6.4 | Há instabilidade conhecida (erros 504 em `/viagens` e `/viagens/{id}`)? Existe SLA ou janela de manutenção? | Observamos 504 intermitentes | B |
| 6.5 | Há ambiente de homologação oficial da API? | Encontramos um domínio `portaldatransparencia-h` | C |
| 6.6 | É permitido carregar o histórico completo pela API ou isso deve ser feito pelo download em lote? | A página oficial recomenda planilhas para o conjunto completo | A |
| 6.7 | Podemos ter mais de uma chave (produção e teste) por organização? A chave expira? | Operação e rotação | C |
| 6.8 | Há restrições de uso ou redistribuição dos dados (licença)? O Decreto 8.777/2016 cobre a gravação em base própria? | Para registrar no projeto | C |

## 7. Paginação e consulta
| # | Pergunta | Por que perguntamos | Prior. |
|---|---|---|---|
| 7.1 | A ordenação entre páginas é estável? O tamanho da página (15) pode ser alterado? | Evitar perda de registro entre páginas; hoje só sabemos que o fim é `[]` | B |
| 7.2 | Há forma de obter o total de registros (contagem) sem paginar? | Hoje o total só é conhecido lendo tudo | B |
| 7.3 | Uma resposta `[]` pode ser transitória? | Tratamos vazio como fim de página | C |

## 8. Download em lote
| # | Pergunta | Por que perguntamos | Prior. |
|---|---|---|---|
| 8.1 | Qual a URL estável de cada arquivo por ano (`/download-de-dados/viagens/{ano}`), o formato, o encoding e o separador? | A página monta a lista por JavaScript; a URL não respondeu a consulta de cabeçalho | A |
| 8.2 | Há checksum, tamanho e data de geração publicados? A atualização é sobrescrita ou há versões? | Para conciliar e detectar mudança | B |
| 8.3 | Há API ou lista de exercícios disponíveis (a página mostra 2011 a 2027)? | Descobrir competência automaticamente | C |

## 9. Mudanças e comunicação
| # | Pergunta | Por que perguntamos | Prior. |
|---|---|---|---|
| 9.1 | Como são comunicadas mudanças de layout, campos novos ou removidos? O changelog da API só tem 2 entradas, ambas de Bolsa Família | Precisamos de aviso antes de mudanças | B |
| 9.2 | Existe versionamento da API (v1, v2) ou política de depreciação? | Estabilidade do contrato | B |
| 9.3 | Qual canal de suporte e prazo de resposta para incidentes? | Operação | C |
| 9.4 | A documentação Swagger e a página oficial listam limites diferentes em outro domínio (90 e 300 req/min no ambiente de homologação). Qual é a fonte da verdade? | Evitar usar limite errado | C |

## 10. Testes realizados (evidências), em 19/10/2026
Chave enviada no header `chave-api-dados`; órgão `33000` (MPS), salvo indicação. Base: `https://api.portaldatransparencia.gov.br/api-de-dados`.

### 10.1 Deram certo
| Teste | Consulta | Resultado |
|---|---|---|
| Autenticação | `GET /viagens` com o header da chave | 200 |
| Janela de 1 mês | ida e retorno em 01/08 a 31/08/2026 | 142 viagens em 10 páginas: 9 páginas com 15, a décima com 7, a 11ª `[]` |
| Fim da paginação | página além da última | `[]` com 200 |
| Mês de ida × mês de retorno | ida em março, retorno em março / abril / junho | 312 / 18 / 3 viagens |
| Cobertura do ano | 156 combinações de ida × retorno (retorno até +12 meses) | 1.460 viagens com ida em 2026; 26 combinações com dados |
| Repetibilidade | varredura completa executada duas vezes | mesmos 1.460 ids, 0 diferenças; agosto repetido: mesmos 142 ids |
| Viagem mais longa | ida 22/02, retorno 22/08 | 181 dias, achada na combinação fevereiro × agosto |
| Janela menor que 1 mês | ida 02–08/03, retorno em março | 94 viagens |
| Janela de um dia (`De` = `Ate`) | ida 04/03 a 04/03, retorno em março | 41 viagens (confere com os dados); 03/03 devolveu 0 e não há viagem nesse dia |
| Limite de dias | 01/03 a 01/04 (31 dias) | aceito, 312 viagens |
| Detalhe por id | `GET /viagens/{id}` em 3 viagens | objeto idêntico ao da lista |
| Entidades do MPS | agosto/2026 em `33000`, `37202`, `33206` | 142, 1.265 e 22 viagens |
| Entidade da Defesa | outubro/2026 em `52131` (Comando da Marinha) | 7 viagens (iguais às da tela do portal) |
| Lista de órgãos | `/orgaos-siafi` e `/orgaos-siape` até `[]` | 766 e 641 órgãos |
| Busca de órgão | `descricao=Previdência` | 4 resultados no SIAFI e 13 no SIAPE |
| Ligação viagem ↔ servidor | `/servidores?nome=...&orgaoServidorExercicio=33100` | 1 servidor; `cpfFormatado` igual ao da viagem |
| Cálculo do total | passagem + diárias + taxa + restituição | confere em 1.434 das 1.460 viagens |
| Limites de uso | carga com pausa de 50% do limite informado | 0 erros nas execuções feitas |

### 10.2 Deram errado ou não retornaram o esperado
| Teste | Consulta | Resultado | Pergunta |
|---|---|---|---|
| Janela de retorno longa | retorno 01/09 a 31/12 (4 meses) | 400 `O período deve ser de no máximo 1 mês.` | 1.7 |
| Janela de 2 meses | retorno 01/09 a 31/10 | 400, mesma mensagem | 1.7 |
| Janela de 32 dias | 01/03 a 02/04 | 400, mesma mensagem | 1.7 |
| Só datas de ida | `dataIdaDe`, `dataIdaAte`, `codigoOrgao`, `pagina` | 400 `Required parameter 'dataRetornoDe' is not present` | 1.6, 1.7 |
| Sem órgão | quatro datas, sem `codigoOrgao` | 400 `Required parameter 'codigoOrgao' is not present` | 2.1 |
| Código `308819` | `codigoOrgao=308819` | 200 com `[]` (sem erro) | 2.2 |
| Código `308819` nos órgãos | `/orgaos-siafi` e `/orgaos-siape` com `codigo=308819` e `30881` | `[]` | 2.2 |
| Ministério como órgão | outubro/2026 em `52000` (Defesa) | só 1 viagem, enquanto a Marinha (`52131`) tem 7 | 2.1 |
| Retorno antes da ida | ida em um mês, retorno 1 a 3 meses antes | `[]` | 1.6 |
| `Ate` anterior a `De` | ida 31/03 a 01/03 | `[]` sem erro | 7.3 |
| Retorno muito depois | ida em jan–jun/2026, retorno 7 meses ou mais depois, e em 2028 | `[]` | 1.6 |
| Total diferente da soma | 26 viagens de 2026 | `valorTotalViagem` maior que a soma dos componentes expostos | 3.1, 3.2 |
| Instabilidade | `/viagens/{id}` | 504 em 4 tentativas seguidas; depois respondeu 200. `/viagens` também deu 504 uma vez | 6.4 |
| Busca de órgão em minúsculas | `descricao=previdencia` | `[]` | 2.4 |
| Busca com acento em maiúsculas | `descricao=PREVIDÊNCIA` | `[]` | 2.4 |
| Leitura automática do portal | `curl` e leitor web em 5 de 7 páginas oficiais | HTTP 405; só abriram no navegador | 9.3 |
| URL do download por ano | consulta de cabeçalho em `/download-de-dados/viagens/2026` pelo navegador | `Failed to fetch` | 8.1 |
| `/viagens-por-cpf` e `/pessoa-fisica` | não testados | exigem CPF completo, que nenhuma resposta fornece | 5.1 |
| Passagens, trechos e pagamentos | procurados na spec de 109 endpoints | não existem na API | 4.1 |

## Informações que levaremos à reunião
- **Resultado atual:** MPS (`33000`), 1.460 viagens com ida em 2026; duas varreduras completas idênticas; 26 totais divergentes pela fórmula.
- **Consulta usada:** janelas de 1 mês, combinando mês de ida × mês de retorno (retorno até 12 meses depois). Foram vistas viagens com retorno até 6 meses depois da ida (máximo de 181 dias).
- **Exemplos para a reunião:** viagens com `valorTotalViagem` diferente da soma dos componentes, e o código `308819`.
