# ADR 0004: nome do beneficiário na camada analítica

Status: Proposto (o PRD 10.1 registra, em 19/10/2026, que o nome segue na analítica; este ADR documenta a razão e as alternativas)

Data: 2026-11-11.

## Contexto

- Hoje `dim_beneficiario` e `obt_viagem` guardam `beneficiario_nome` e `cpf_mascarado`. A chave do beneficiário é um hash de nome + CPF parcial (homônimos são uma pendência conhecida).
- O CPF vem mascarado da API (`***.947.711-**`) e é mantido assim em todas as camadas; não existe CPF completo em lugar nenhum e não se tenta reconstruí-lo.
- Viagens sigilosas chegam com o nome "Informações protegidas por sigilo"; o próprio Portal já protege esses casos na origem.
- Os dados são públicos: o Portal da Transparência publica nome, cargo, motivo e valores das viagens a serviço (livre utilização, Decreto 8.777/2016), e o download oficial traz CPF parcial e nome.
- O campo `motivo` (texto livre) já saiu da analítica por poder conter dado pessoal (PRD 10.1). A pergunta é se o nome também deve sair ou ser transformado.

## LGPD

Dado público não deixa de ser dado pessoal: a LGPD (Lei 13.709/2018) continua exigindo finalidade, necessidade e minimização. O tratamento pelo órgão tem base legal (publicidade e transparência ativa) para a finalidade original; um painel que cruza o nome com outros dados e é lido por mais pessoas é outro uso e pede o mesmo cuidado. O risco principal é a analítica ser a camada de consumo, exposta a ferramentas e usuários de BI com acessos amplos. O papel de leitura (`papel_leitura.sql`) limita quem lê, mas não o conteúdo.

## Opções

1. **Manter o nome** em `dim_beneficiario` e `obt_viagem`.
   - Impacto: nenhum no modelo; o painel mostra quem viajou. A `obt_viagem` carrega o nome em cada linha, o que aumenta a exposição.
2. **Pseudonimizar:** guardar na analítica só um identificador (hash já existente) e um rótulo parcial; o nome fica na intermediária.
   - Impacto: `dim_beneficiario` perde `beneficiario_nome` (ou passa a ter iniciais); `obt_viagem` perde a coluna; análise por pessoa continua possível pela chave, sem nome. O painel não mostra o nome. Exige mudar DDL, carga e views.
3. **Remover o nome** da analítica.
   - Impacto: `dim_beneficiario` fica sem nome e quase sem utilidade (chave e CPF parcial); `obt_viagem` sem a coluna. Menor risco; perde a análise por pessoa e a conferência com o Portal.

## Recomendação

Opção 1 (manter), com as mitigações já em vigor: CPF sempre mascarado, `motivo` fora da analítica, nome vindo "protegido" nas viagens sigilosas, acesso à analítica por papel de leitura e nenhum cruzamento com dados externos. Isso coincide com a decisão do PRD 10.1. Se o painel nunca precisar exibir o nome de pessoas, a opção 2 é a escolha mais segura e vale reavaliar; o encarregado de dados (DPO) do órgão deve opinar. A decisão final é do dono do projeto.

## Alternativas rejeitadas

- **Remover o nome (opção 3):** rejeitada por ora; elimina o uso por pessoa (por exemplo, a conferência com o Portal) sem necessidade comprovada.
- **Tentar reconstruir o CPF completo:** rejeitada; aumentaria o risco LGPD sem ganho, e a API não fornece.

## Consequencias

- Manter o nome mantém a necessidade de controle de acesso: a analítica deve ser lida só pelo papel de leitura, e o `obt_viagem` não deve ser exportado sem avaliação.
- Mudar para a opção 2 ou 3 exige alterar `schema.sql` (`dim_beneficiario`, `obt_viagem` e os `COMMENT ON`), a carga analítica, as views de KPI e os testes, e uma reconstrução da analítica (`--reconstruir-silver`).
- A intermediária e a staging seguem com o nome (a staging guarda o JSON como recebido); o risco só cai de fato se o acesso a essas camadas for restrito.
- Nenhum schema é alterado por este documento.
