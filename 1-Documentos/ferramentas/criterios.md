# Critérios para escolher ferramentas

Peso de 1 (pouco importante) a 5 (decisivo). Este documento define os critérios; não pontua nenhuma ferramenta. Usado por `comparativo-alerta.md` e por futuras escolhas (por exemplo, o canal de alerta do ADR 0003).

| Critério | Peso | Justificativa |
|---|---|---|
| Custo | 4 | Projeto de órgão público sem orçamento próprio para licenças; custo recorrente precisa de aprovação |
| Licenca | 4 | Precisa permitir uso em órgão público, sem cláusula que impeça servidor próprio ou código aberto; preferência por licenças abertas (o Airflow é Apache 2.0) |
| Integração com Postgres | 5 | Toda a carga está em PostgreSQL (modelo medalhão, schemas `staging`, `intermediaria` e `analitica`); a ferramenta deve ler Postgres sem intermediário |
| Integração com o Airflow | 4 | A orquestração é Airflow 2.10; a ferramenta deve ser chamada por tarefa ou callback sem dependência pesada |
| Segurança de segredos | 5 | A chave da API e a senha do banco não podem ir para o repositório, log ou mensagem; a ferramenta deve aceitar segredo por ambiente, Connection ou Variable |
| LGPD | 5 | Há nome e CPF parcial de servidores; a ferramenta não pode enviar dado pessoal para fora do órgão sem base legal, nem ampliar o acesso |
| Hospedagem | 3 | Onde roda: servidor do órgão ou nuvem; saída de rede e política de TI limitam as opções |
| Esforço de operação | 4 | Equipe pequena; menos peças para atualizar, monitorar e restaurar |
| Curva de aprendizado | 2 | Importa na adoção, mas é um custo pontual; pesa menos que operação contínua |
| Suporte e manutenção | 3 | Projeto ativo, documentação e comunidade; risco de abandono |
| Confiabilidade | 4 | Uma falha da ferramenta não pode derrubar a carga nem esconder erro |

## Como usar

Cada ferramenta recebe nota de 1 a 5 em cada critério e a soma é ponderada pelo peso. Critérios eliminatórios (antes da soma): não guardar segredo no repositório, não enviar dado pessoal sem base legal, não exigir licença paga não aprovada. Afirmações sobre uma ferramenta devem ter fonte; o que depende de política do órgão fica marcado como "a confirmar".
