# Referência da API do Portal da Transparência (gerada da spec /v3/api-docs)

109 endpoints. Tags: Benefícios, Contratos do Poder Executivo Federal, Convênios do Poder Executivo Federal, Coronavírus, Despesas Públicas, Emendas parlamentares, Gastos por meio de cartão de pagamento, Imóveis Funcionais, Licitações do Poder Executivo Federal, Notas Fiscais, Pessoas físicas e jurídicas, Renúncias Fiscais, Sanções, Servidores do Poder Executivo Federal, Viagens a serviço, api-funcional-programatica-controller, Órgãos


## Benefícios

### GET /api-de-dados/seguro-defeso-por-municipio
Consulta os registros Seguro Defeso — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BeneficioPorMunicipioDTO): id:integer, dataReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, tipo:obj, tipo.id:integer, tipo.descricao:string, tipo.descricaoDetalhada:string, valor:number, quantidadeBeneficiados:integer

### GET /api-de-dados/seguro-defeso-codigo
Consulta os registros Seguro Defeso por CPF/NIS — Filtros mínimos:  Página (padrão = 1);  CPF / NIS;
- `codigo` (obrigatório): CPF/NIS
- `pagina` (obrigatório): Página consultada
- Resposta (lista de SeguroDefesoDTO): id:integer, pessoaSeguroDefeso:obj, pessoaSeguroDefeso.cpfFormatado:string, pessoaSeguroDefeso.nis:string, pessoaSeguroDefeso.nome:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, portaria:string, dataMesReferencia:string, dataSaque:string, dataEmissaoParcela:string, situacao:string, rgp:string, parcela:string, valor:number

### GET /api-de-dados/seguro-defeso-beneficiario-por-municipio
Consulta os registros Seguro Defeso dos Beneficiários por Município e Mes/Ano — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de SeguroDefesoDTO): id:integer, pessoaSeguroDefeso:obj, pessoaSeguroDefeso.cpfFormatado:string, pessoaSeguroDefeso.nis:string, pessoaSeguroDefeso.nome:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, portaria:string, dataMesReferencia:string, dataSaque:string, dataEmissaoParcela:string, situacao:string, rgp:string, parcela:string, valor:number

### GET /api-de-dados/safra-por-municipio
Consulta os registros Garantia-Safra — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BeneficioPorMunicipioDTO): id:integer, dataReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, tipo:obj, tipo.id:integer, tipo.descricao:string, tipo.descricaoDetalhada:string, valor:number, quantidadeBeneficiados:integer

### GET /api-de-dados/safra-codigo-por-cpf-ou-nis
Consulta os registros Garantia-Safra por CPF/NIS — Filtros mínimos:  Página (padrão = 1);  CPF / NIS;
- `codigo` (obrigatório): CPF/NIS
- `pagina` (obrigatório): Página consultada
- Resposta (lista de SafraDTO): id:integer, beneficiarioSafra:obj, beneficiarioSafra.cpfFormatado:string, beneficiarioSafra.nis:string, beneficiarioSafra.nome:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, valor:number

### GET /api-de-dados/safra-beneficiario-por-municipio
Consulta os registros Garantia-Safra dos beneficiários por município e mes/ano — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de SafraDTO): id:integer, beneficiarioSafra:obj, beneficiarioSafra.cpfFormatado:string, beneficiarioSafra.nis:string, beneficiarioSafra.nome:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, valor:number

### GET /api-de-dados/peti-por-municipio
Consulta os registros Programa de Erradicação do Trabalho Infantil — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BeneficioPorMunicipioDTO): id:integer, dataReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, tipo:obj, tipo.id:integer, tipo.descricao:string, tipo.descricaoDetalhada:string, valor:number, quantidadeBeneficiados:integer

### GET /api-de-dados/peti-por-cpf-ou-nis
Consulta os registros Programa de Erradicação do Trabalho Infantil por CPF/NIS — Filtros mínimos:  Página (padrão = 1);  CPF / NIS;
- `codigo` (obrigatório): CPF/NIS
- `pagina` (obrigatório): Página consultada
- Resposta (lista de PetiDTO): id:integer, beneficiarioPeti:obj, beneficiarioPeti.cpfFormatado:string, beneficiarioPeti.nis:string, beneficiarioPeti.nome:string, dataDisponibilizacaoRecurso:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, situacao:string, valor:number

### GET /api-de-dados/peti-beneficiario-por-municipio
Consulta os registros PETI dos beneficiários por município e mês/ano — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de PetiDTO): id:integer, beneficiarioPeti:obj, beneficiarioPeti.cpfFormatado:string, beneficiarioPeti.nis:string, beneficiarioPeti.nome:string, dataDisponibilizacaoRecurso:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, situacao:string, valor:number

### GET /api-de-dados/novo-bolsa-familia-sacado-por-nis
 — 
- `nis` (obrigatório): 
- `anoMesReferencia`: 
- `anoMesCompetencia`: 
- `pagina`: 
- Resposta (lista de NovoBolsaFamiliaPagoDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, beneficiarioNovoBolsaFamilia:obj, beneficiarioNovoBolsaFamilia.cpfFormatado:string, beneficiarioNovoBolsaFamilia.nis:string, beneficiarioNovoBolsaFamilia.nome:string, valorSaque:number

### GET /api-de-dados/novo-bolsa-familia-sacado-por-cpf-ou-nis
 — 
- `codigo` (obrigatório): 
- `anoMesReferencia`: 
- `anoMesCompetencia`: 
- `pagina`: 
- Resposta (lista de NovoBolsaFamiliaPagoDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, beneficiarioNovoBolsaFamilia:obj, beneficiarioNovoBolsaFamilia.cpfFormatado:string, beneficiarioNovoBolsaFamilia.nis:string, beneficiarioNovoBolsaFamilia.nome:string, valorSaque:number

### GET /api-de-dados/novo-bolsa-familia-sacado-beneficiario-por-municipio
 — 
- `mesAno` (obrigatório): 
- `codigoIbge` (obrigatório): 
- `pagina`: 
- Resposta (lista de NovoBolsaFamiliaPagoDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, beneficiarioNovoBolsaFamilia:obj, beneficiarioNovoBolsaFamilia.cpfFormatado:string, beneficiarioNovoBolsaFamilia.nis:string, beneficiarioNovoBolsaFamilia.nome:string, valorSaque:number

### GET /api-de-dados/novo-bolsa-familia-por-municipio
 — 
- `mesAno` (obrigatório): 
- `codigoIbge` (obrigatório): 
- `pagina`: 
- Resposta (lista de BeneficioPorMunicipioDTO): id:integer, dataReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, tipo:obj, tipo.id:integer, tipo.descricao:string, tipo.descricaoDetalhada:string, valor:number, quantidadeBeneficiados:integer

### GET /api-de-dados/bpc-por-municipio
Consulta os registros de Benefício de Prestação Continuada por Município — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BeneficioPorMunicipioDTO): id:integer, dataReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, tipo:obj, tipo.id:integer, tipo.descricao:string, tipo.descricaoDetalhada:string, valor:number, quantidadeBeneficiados:integer

### GET /api-de-dados/bpc-por-cpf-ou-nis
Consulta os registros de Benefício de Prestação Continuada por CPF/NIS — Filtros mínimos:  Página (padrão = 1);  CPF / NIS;
- `codigo` (obrigatório): CPF/NIS
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BPCDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, beneficiario:obj, beneficiario.cpfFormatado:string, beneficiario.nis:string, beneficiario.nome:string, beneficiario.cpfRepresentanteLegalFormatado:string, beneficiario.nisRepresentanteLegal:string, beneficiario.nomeRepresentanteLegal:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, valor:number, concedidoJudicialmente:boolean, menor16anos:boolean

### GET /api-de-dados/bpc-beneficiario-por-municipio
Consulta os registros de Benefício de Prestação Continuada dos Beneficiários por Município e Mes/Ano — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BPCDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, beneficiario:obj, beneficiario.cpfFormatado:string, beneficiario.nis:string, beneficiario.nome:string, beneficiario.cpfRepresentanteLegalFormatado:string, beneficiario.nisRepresentanteLegal:string, beneficiario.nomeRepresentanteLegal:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, valor:number, concedidoJudicialmente:boolean, menor16anos:boolean

### GET /api-de-dados/bolsa-familia-sacado-por-nis
Consulta as parcelas sacadas pelo Bolsa Família pelo NIS — Filtros mínimos:  Página (padrão = 1);  NIS; Ano e mês de competência (AAAAMM) ou Ano e mês de referência (AAAAMM);
- `nis` (obrigatório): NIS (sem máscara, somente números)
- `anoMesReferencia`: Ano e mês de referência (AAAAMM)
- `anoMesCompetencia`: Ano e mês de competência (AAAAMM)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BolsaFamiliaPagoDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, beneficiarioBolsaFamilia:obj, beneficiarioBolsaFamilia.cpfFormatado:string, beneficiarioBolsaFamilia.nis:string, beneficiarioBolsaFamilia.nome:string, dataSaque:string, valorSaque:number

### GET /api-de-dados/bolsa-familia-sacado-por-cpf-ou-nis
Consulta as parcelas sacadas pelo Bolsa Família pelo CPF/NIS — Filtros mínimos:  Página (padrão = 1);  NIS; Ano e mês de competência (AAAAMM) ou Ano e mês de referência (AAAAMM);
- `codigo` (obrigatório): CPF/NIS (sem máscara, somente números)
- `anoMesReferencia`: Ano e mês de referência (AAAAMM)
- `anoMesCompetencia`: Ano e mês de competência (AAAAMM)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BolsaFamiliaPagoDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, beneficiarioBolsaFamilia:obj, beneficiarioBolsaFamilia.cpfFormatado:string, beneficiarioBolsaFamilia.nis:string, beneficiarioBolsaFamilia.nome:string, dataSaque:string, valorSaque:number

### GET /api-de-dados/bolsa-familia-sacado-beneficiario-por-municipio
Consulta as parcelas do Bolsa Família Sacado dos Beneficiários por Município e Mes/Ano — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BolsaFamiliaPagoDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, beneficiarioBolsaFamilia:obj, beneficiarioBolsaFamilia.cpfFormatado:string, beneficiarioBolsaFamilia.nis:string, beneficiarioBolsaFamilia.nome:string, dataSaque:string, valorSaque:number

### GET /api-de-dados/bolsa-familia-por-municipio
Consulta as parcelas do Bolsa Família por Município — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BeneficioPorMunicipioDTO): id:integer, dataReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, tipo:obj, tipo.id:integer, tipo.descricao:string, tipo.descricaoDetalhada:string, valor:number, quantidadeBeneficiados:integer

### GET /api-de-dados/bolsa-familia-disponivel-por-cpf-ou-nis
Consulta as parcelas disponibilizadas pelo Bolsa Família pelo CPF/NIS — Filtros mínimos:  Página (padrão = 1);  CPF / NIS;  Ano e mês de competência (AAAAMM) ou Ano e mês de referência (AAAAMM);
- `codigo` (obrigatório): CPF/NIS (sem máscara, somente números)
- `anoMesReferencia`: Ano e mês de referência (AAAAMM)
- `anoMesCompetencia`: Ano e mês de competência (AAAAMM)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BolsaFamiliaDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, titularBolsaFamilia:obj, titularBolsaFamilia.cpfFormatado:string, titularBolsaFamilia.nis:string, titularBolsaFamilia.nome:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, valor:number, quantidadeDependentes:integer

### GET /api-de-dados/bolsa-familia-disponivel-beneficiario-por-municipio
Consulta as parcelas do Bolsa Família Disponível dos Beneficiários por Município e Mes/Ano — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BolsaFamiliaDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, titularBolsaFamilia:obj, titularBolsaFamilia.cpfFormatado:string, titularBolsaFamilia.nis:string, titularBolsaFamilia.nome:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, valor:number, quantidadeDependentes:integer

### GET /api-de-dados/auxilio-emergencial-por-municipio
Consulta os registros de auxílio emergencial por Município — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BeneficioPorMunicipioDTO): id:integer, dataReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, tipo:obj, tipo.id:integer, tipo.descricao:string, tipo.descricaoDetalhada:string, valor:number, quantidadeBeneficiados:integer

### GET /api-de-dados/auxilio-emergencial-por-cpf-ou-nis
Consulta os registros de auxílio emergencial por CPF/NIS — Filtros mínimos:  Página (padrão = 1);  CPF / NIS;
- `codigoBeneficiario`: CPF/NIS Beneficiário
- `codigoResponsavelFamiliar`: CPF/NIS Responsável Familiar
- `pagina` (obrigatório): Página consultada
- Resposta (lista de AuxilioEmergencialDTO): id:integer, mesDisponibilizacao:string, beneficiario:obj, beneficiario.cpfFormatado:string, beneficiario.nis:string, beneficiario.nome:string, responsavelAuxilioEmergencial:obj, responsavelAuxilioEmergencial.cpfFormatado:string, responsavelAuxilioEmergencial.nis:string, responsavelAuxilioEmergencial.nome:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, situacaoAuxilioEmergencial:string, enquadramentoAuxilioEmergencial:string, valor:number, numeroParcela:string

### GET /api-de-dados/auxilio-emergencial-beneficiario-por-municipio
Consulta os registros dos beneficiários por município e mês/ano — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de AuxilioEmergencialDTO): id:integer, mesDisponibilizacao:string, beneficiario:obj, beneficiario.cpfFormatado:string, beneficiario.nis:string, beneficiario.nome:string, responsavelAuxilioEmergencial:obj, responsavelAuxilioEmergencial.cpfFormatado:string, responsavelAuxilioEmergencial.nis:string, responsavelAuxilioEmergencial.nome:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, situacaoAuxilioEmergencial:string, enquadramentoAuxilioEmergencial:string, valor:number, numeroParcela:string

### GET /api-de-dados/auxilio-brasil-sacado-por-nis
Consulta as parcelas disponibilizadas pelo Auxílio Brasil pelo NIS — Filtros mínimos:  Página (padrão = 1);  NIS; Ano e mês de competência (AAAAMM) ou Ano e mês de referência (AAAAMM);
- `nis` (obrigatório): NIS (sem máscara, somente números)
- `anoMesReferencia`: Ano e mês de referência (AAAAMM)
- `anoMesCompetencia`: Ano e mês de competência (AAAAMM)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de AuxilioBrasilPagoDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, beneficiarioAuxilioBrasil:obj, beneficiarioAuxilioBrasil.cpfFormatado:string, beneficiarioAuxilioBrasil.nis:string, beneficiarioAuxilioBrasil.nome:string, dataSaque:string, valorSaque:number

### GET /api-de-dados/auxilio-brasil-sacado-por-cpf-ou-nis
Consulta as parcelas disponibilizadas pelo Auxílio Brasil pelo CPF/NIS — Filtros mínimos:  Página (padrão = 1);  CPF/NIS; Ano e mês de competência (AAAAMM) ou Ano e mês de referência (AAAAMM);
- `codigo` (obrigatório): CPF/NIS (sem máscara, somente números)
- `anoMesReferencia`: Ano e mês de referência (AAAAMM)
- `anoMesCompetencia`: Ano e mês de competência (AAAAMM)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de AuxilioBrasilPagoDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, beneficiarioAuxilioBrasil:obj, beneficiarioAuxilioBrasil.cpfFormatado:string, beneficiarioAuxilioBrasil.nis:string, beneficiarioAuxilioBrasil.nome:string, dataSaque:string, valorSaque:number

### GET /api-de-dados/auxilio-brasil-sacado-beneficiario-por-municipio
Consulta as parcelas do Auxílio Brasil Sacado dos Beneficiários por Município e Mes/Ano — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de AuxilioBrasilPagoDTO): id:integer, dataMesCompetencia:string, dataMesReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, beneficiarioAuxilioBrasil:obj, beneficiarioAuxilioBrasil.cpfFormatado:string, beneficiarioAuxilioBrasil.nis:string, beneficiarioAuxilioBrasil.nome:string, dataSaque:string, valorSaque:number

### GET /api-de-dados/auxilio-brasil-por-municipio
Consulta as parcelas do Auxílio Brasil por Município — Filtros mínimos:  Página (padrão = 1);  Ano/Mês (YYYYMM); Código IBGE (https://cidades.ibge.gov.br/brasil);
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `codigoIbge` (obrigatório): Código IBGE
- `pagina` (obrigatório): Página consultada
- Resposta (lista de BeneficioPorMunicipioDTO): id:integer, dataReferencia:string, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, tipo:obj, tipo.id:integer, tipo.descricao:string, tipo.descricaoDetalhada:string, valor:number, quantidadeBeneficiados:integer

## Contratos do Poder Executivo Federal

### GET /api-de-dados/contratos
Consulta os todos contratos do Poder Executivo Federal — Filtros mínimos:  Página (padrão = 1); Código do Órgão (SIAFI); Data vigência início; Data vigência fim
- `dataInicial`: Data vigência início (DD/MM/AAAA)
- `dataFinal`: Data vigência fim (DD/MM/AAAA)
- `codigoOrgao` (obrigatório): Código do Órgão (SIAFI)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ContratoDTO): id:integer, numero:string, objeto:string, numeroProcesso:string, fundamentoLegal:string, compra:obj, compra.numero:string, compra.objeto:string, compra.numeroProcesso:string, compra.contatoResponsavel:string, situacaoContrato:string, modalidadeCompra:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, unidadeGestoraCompras:obj, unidadeGestoraCompras.codigo:string, unidadeGestoraCompras.nome:string, unidadeGestoraCompras.descricaoPoder:string, unidadeGestoraCompras.orgaoVinculado:obj, unidadeGestoraCompras.orgaoVinculado.codigoSIAFI:string, unidadeGestoraCompras.orgaoVinculado.cnpj:string, unidadeGestoraCompras.orgaoVinculado.sigla:string, unidadeGestoraCompras.orgaoVinculado.nome:string, unidadeGestoraCompras.orgaoMaximo:obj, unidadeGestoraCompras.orgaoMaximo.codigo:string, unidadeGestoraCompras.orgaoMaximo.sigla:string, unidadeGestoraCompras.orgaoMaximo.nome:string, dataAssinatura:string, dataPublicacaoDOU:string, dataInicioVigencia:string, dataFimVigencia:string, fornecedor:obj, fornecedor.id:integer, fornecedor.cpfFormatado:string, fornecedor.cnpjFormatado:string, fornecedor.numeroInscricaoSocial:string, fornecedor.nome:string, fornecedor.razaoSocialReceita:string, fornecedor.nomeFantasiaReceita:string, fornecedor.tipo:string, valorInicialCompra:number, valorFinalCompra:number

### GET /api-de-dados/contratos/termo-aditivo
Consulta os termos aditivos do contrato pelo id do contrato — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (lista de TermoAditivoDTO): numero:string, dataPublicacao:string, objetoAditivo:string

### GET /api-de-dados/contratos/processo
Consulta um contrato do Poder Executivo Federal pelo número do processo — Filtros mínimos:  Página (padrão = 1);  Processo;
- `processo` (obrigatório): Número do processo
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ContratoDTO): id:integer, numero:string, objeto:string, numeroProcesso:string, fundamentoLegal:string, compra:obj, compra.numero:string, compra.objeto:string, compra.numeroProcesso:string, compra.contatoResponsavel:string, situacaoContrato:string, modalidadeCompra:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, unidadeGestoraCompras:obj, unidadeGestoraCompras.codigo:string, unidadeGestoraCompras.nome:string, unidadeGestoraCompras.descricaoPoder:string, unidadeGestoraCompras.orgaoVinculado:obj, unidadeGestoraCompras.orgaoVinculado.codigoSIAFI:string, unidadeGestoraCompras.orgaoVinculado.cnpj:string, unidadeGestoraCompras.orgaoVinculado.sigla:string, unidadeGestoraCompras.orgaoVinculado.nome:string, unidadeGestoraCompras.orgaoMaximo:obj, unidadeGestoraCompras.orgaoMaximo.codigo:string, unidadeGestoraCompras.orgaoMaximo.sigla:string, unidadeGestoraCompras.orgaoMaximo.nome:string, dataAssinatura:string, dataPublicacaoDOU:string, dataInicioVigencia:string, dataFimVigencia:string, fornecedor:obj, fornecedor.id:integer, fornecedor.cpfFormatado:string, fornecedor.cnpjFormatado:string, fornecedor.numeroInscricaoSocial:string, fornecedor.nome:string, fornecedor.razaoSocialReceita:string, fornecedor.nomeFantasiaReceita:string, fornecedor.tipo:string, valorInicialCompra:number, valorFinalCompra:number

### GET /api-de-dados/contratos/numero
Consulta um contrato do Poder Executivo Federal pelo número do contrato — Filtros mínimos:  Página (padrão = 1);  Número;
- `numero` (obrigatório): Número do contrato
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ContratoDTO): id:integer, numero:string, objeto:string, numeroProcesso:string, fundamentoLegal:string, compra:obj, compra.numero:string, compra.objeto:string, compra.numeroProcesso:string, compra.contatoResponsavel:string, situacaoContrato:string, modalidadeCompra:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, unidadeGestoraCompras:obj, unidadeGestoraCompras.codigo:string, unidadeGestoraCompras.nome:string, unidadeGestoraCompras.descricaoPoder:string, unidadeGestoraCompras.orgaoVinculado:obj, unidadeGestoraCompras.orgaoVinculado.codigoSIAFI:string, unidadeGestoraCompras.orgaoVinculado.cnpj:string, unidadeGestoraCompras.orgaoVinculado.sigla:string, unidadeGestoraCompras.orgaoVinculado.nome:string, unidadeGestoraCompras.orgaoMaximo:obj, unidadeGestoraCompras.orgaoMaximo.codigo:string, unidadeGestoraCompras.orgaoMaximo.sigla:string, unidadeGestoraCompras.orgaoMaximo.nome:string, dataAssinatura:string, dataPublicacaoDOU:string, dataInicioVigencia:string, dataFimVigencia:string, fornecedor:obj, fornecedor.id:integer, fornecedor.cpfFormatado:string, fornecedor.cnpjFormatado:string, fornecedor.numeroInscricaoSocial:string, fornecedor.nome:string, fornecedor.razaoSocialReceita:string, fornecedor.nomeFantasiaReceita:string, fornecedor.tipo:string, valorInicialCompra:number, valorFinalCompra:number

### GET /api-de-dados/contratos/itens-contratados
Consulta os itens contratados pelo id do contrato — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ItemContratadoDTO): numero:string, descricao:string, quantidade:integer, valor:string, descComplementarItemCompra:string

### GET /api-de-dados/contratos/id
Consulta um contrato do Poder Executivo Federal pelo id — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (objeto de ContratoDTO): id:integer, numero:string, objeto:string, numeroProcesso:string, fundamentoLegal:string, compra:obj, compra.numero:string, compra.objeto:string, compra.numeroProcesso:string, compra.contatoResponsavel:string, situacaoContrato:string, modalidadeCompra:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, unidadeGestoraCompras:obj, unidadeGestoraCompras.codigo:string, unidadeGestoraCompras.nome:string, unidadeGestoraCompras.descricaoPoder:string, unidadeGestoraCompras.orgaoVinculado:obj, unidadeGestoraCompras.orgaoVinculado.codigoSIAFI:string, unidadeGestoraCompras.orgaoVinculado.cnpj:string, unidadeGestoraCompras.orgaoVinculado.sigla:string, unidadeGestoraCompras.orgaoVinculado.nome:string, unidadeGestoraCompras.orgaoMaximo:obj, unidadeGestoraCompras.orgaoMaximo.codigo:string, unidadeGestoraCompras.orgaoMaximo.sigla:string, unidadeGestoraCompras.orgaoMaximo.nome:string, dataAssinatura:string, dataPublicacaoDOU:string, dataInicioVigencia:string, dataFimVigencia:string, fornecedor:obj, fornecedor.id:integer, fornecedor.cpfFormatado:string, fornecedor.cnpjFormatado:string, fornecedor.numeroInscricaoSocial:string, fornecedor.nome:string, fornecedor.razaoSocialReceita:string, fornecedor.nomeFantasiaReceita:string, fornecedor.tipo:string, valorInicialCompra:number, valorFinalCompra:number

### GET /api-de-dados/contratos/documentos-relacionados
Consulta os documentos relacionados a um contrato pelo id do contrato — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (lista de EmpenhoComprasDTO): empenho:string, empenhoResumido:string, dataEmissao:string, observacao:string, valor:string

### GET /api-de-dados/contratos/cpf-cnpj
Consulta um contrato do Poder Executivo Federal pelo CPF/CNPJ do Fornecedor — Filtros mínimos: CPF/CNPJ do Fornecedor
- `cpfCnpj` (obrigatório): CPF/CNPJ do Fornecedor
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ContratoDTO): id:integer, numero:string, objeto:string, numeroProcesso:string, fundamentoLegal:string, compra:obj, compra.numero:string, compra.objeto:string, compra.numeroProcesso:string, compra.contatoResponsavel:string, situacaoContrato:string, modalidadeCompra:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, unidadeGestoraCompras:obj, unidadeGestoraCompras.codigo:string, unidadeGestoraCompras.nome:string, unidadeGestoraCompras.descricaoPoder:string, unidadeGestoraCompras.orgaoVinculado:obj, unidadeGestoraCompras.orgaoVinculado.codigoSIAFI:string, unidadeGestoraCompras.orgaoVinculado.cnpj:string, unidadeGestoraCompras.orgaoVinculado.sigla:string, unidadeGestoraCompras.orgaoVinculado.nome:string, unidadeGestoraCompras.orgaoMaximo:obj, unidadeGestoraCompras.orgaoMaximo.codigo:string, unidadeGestoraCompras.orgaoMaximo.sigla:string, unidadeGestoraCompras.orgaoMaximo.nome:string, dataAssinatura:string, dataPublicacaoDOU:string, dataInicioVigencia:string, dataFimVigencia:string, fornecedor:obj, fornecedor.id:integer, fornecedor.cpfFormatado:string, fornecedor.cnpjFormatado:string, fornecedor.numeroInscricaoSocial:string, fornecedor.nome:string, fornecedor.razaoSocialReceita:string, fornecedor.nomeFantasiaReceita:string, fornecedor.tipo:string, valorInicialCompra:number, valorFinalCompra:number

### GET /api-de-dados/contratos/apostilamento
Consulta os apostilamentos do contrato pelo id do contrato — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (lista de ApostilamentoDTO): numero:string, descricao:string, dataInclusao:string, situacao:string, valor:string

## Convênios do Poder Executivo Federal

### GET /api-de-dados/convenios
Consulta todos convênios do Poder Executivo Federal — Filtros mínimos:  Página (padrão = 1);  Período de no máximo 1 dia;
- `dataInicial`: Data referência início (DD/MM/AAAA)
- `dataFinal`: Data referência fim (DD/MM/AAAA)
- `dataUltimaLiberacaoInicial`: Data da última liberação de recurso início (DD/MM/AAAA)
- `dataUltimaLiberacaoFinal`: Data da última liberação de recurso fim (DD/MM/AAAA)
- `dataVigenciaInicial`: Data de vigência início (DD/MM/AAAA)
- `dataVigenciaFinal`: Data de vigência fim (DD/MM/AAAA)
- `convenente`: Convenente
- `tipoConvenente`: Tipo de Convenente
- `numero`: Número do convênio
- `numeroOriginal`: Número original do convênio
- `codigoOrgao`: Código do Órgão (SIAFI)
- `uf`: Sigla UF
- `codigoIBGE`: Município (Código IBGE)
- `situacao`: Código Situação
- `tipoInstrumento`: Código Tipo de Instrumento
- `funcao`: Código Função
- `subfuncao`: Código Subfunção
- `valorLiberadoDe`: Valor liberado de (Formato: 1.000,00)
- `valorLiberadoAte`: Valor liberado até (Formato: 1.000,00)
- `valorTotalDe`: Valor total de (Formato: 1.000,00)
- `valorTotalAte`: Valor total até (Formato: 1.000,00)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ConvenioDTO): id:integer, dataReferencia:string, dataInicioVigencia:string, dataFinalVigencia:string, dataPublicacao:string, dataUltimaLiberacao:string, dataConclusao:string, dimConvenio:obj, dimConvenio.codigo:string, dimConvenio.objeto:string, dimConvenio.numero:string, situacao:string, convenente:obj, convenente.id:integer, convenente.cpfFormatado:string, convenente.cnpjFormatado:string, convenente.numeroInscricaoSocial:string, convenente.nome:string, convenente.razaoSocialReceita:string, convenente.nomeFantasiaReceita:string, convenente.tipo:string, localidadePessoa:obj, localidadePessoa.id:integer, localidadePessoa.descricao:string, municipioConvenente:obj, municipioConvenente.codigoIBGE:string, municipioConvenente.nomeIBGE:string, municipioConvenente.codigoRegiao:string, municipioConvenente.nomeRegiao:string, municipioConvenente.pais:string, municipioConvenente.uf:obj, municipioConvenente.uf.sigla:string, municipioConvenente.uf.nome:string, orgao:obj, orgao.nome:string, orgao.codigoSIAFI:string, orgao.cnpj:string, orgao.sigla:string, orgao.descricaoPoder:string, orgao.orgaoMaximo:obj, orgao.orgaoMaximo.codigo:string, orgao.orgaoMaximo.sigla:string, orgao.orgaoMaximo.nome:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, subfuncao:obj, subfuncao.codigoSubfuncao:string, subfuncao.descricaoSubfuncap:string, subfuncao.funcao:obj, subfuncao.funcao.codigoFuncao:string, subfuncao.funcao.descricaoFuncao:string, tipoInstrumento:obj, tipoInstrumento.id:integer, tipoInstrumento.codigo:string, tipoInstrumento.descricao:string, valor:number, valorLiberado:number, valorContrapartida:number, valorDaUltimaLiberacao:number, numeroProcesso:string

### GET /api-de-dados/convenios/tipo-instrumento
Consulta os tipos de instrumentos usados nos convênios — 
- Resposta (lista de TipoInstrumentoDTO): id:integer, codigo:string, descricao:string

### GET /api-de-dados/convenios/numero
Consulta um convênio do Poder Executivo Federal pelo número do contrato — Filtros mínimos:  Página (padrão = 1);  Número;
- `numero` (obrigatório): Número do convênio
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ConvenioDTO): id:integer, dataReferencia:string, dataInicioVigencia:string, dataFinalVigencia:string, dataPublicacao:string, dataUltimaLiberacao:string, dataConclusao:string, dimConvenio:obj, dimConvenio.codigo:string, dimConvenio.objeto:string, dimConvenio.numero:string, situacao:string, convenente:obj, convenente.id:integer, convenente.cpfFormatado:string, convenente.cnpjFormatado:string, convenente.numeroInscricaoSocial:string, convenente.nome:string, convenente.razaoSocialReceita:string, convenente.nomeFantasiaReceita:string, convenente.tipo:string, localidadePessoa:obj, localidadePessoa.id:integer, localidadePessoa.descricao:string, municipioConvenente:obj, municipioConvenente.codigoIBGE:string, municipioConvenente.nomeIBGE:string, municipioConvenente.codigoRegiao:string, municipioConvenente.nomeRegiao:string, municipioConvenente.pais:string, municipioConvenente.uf:obj, municipioConvenente.uf.sigla:string, municipioConvenente.uf.nome:string, orgao:obj, orgao.nome:string, orgao.codigoSIAFI:string, orgao.cnpj:string, orgao.sigla:string, orgao.descricaoPoder:string, orgao.orgaoMaximo:obj, orgao.orgaoMaximo.codigo:string, orgao.orgaoMaximo.sigla:string, orgao.orgaoMaximo.nome:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, subfuncao:obj, subfuncao.codigoSubfuncao:string, subfuncao.descricaoSubfuncap:string, subfuncao.funcao:obj, subfuncao.funcao.codigoFuncao:string, subfuncao.funcao.descricaoFuncao:string, tipoInstrumento:obj, tipoInstrumento.id:integer, tipoInstrumento.codigo:string, tipoInstrumento.descricao:string, valor:number, valorLiberado:number, valorContrapartida:number, valorDaUltimaLiberacao:number, numeroProcesso:string

### GET /api-de-dados/convenios/numero-processo
Consulta um convênio do Poder Executivo Federal pelo número do processo — Filtros mínimos:  Página (padrão = 1);  Número do processo;
- `numeroProcesso` (obrigatório): Número do processo
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ConvenioDTO): id:integer, dataReferencia:string, dataInicioVigencia:string, dataFinalVigencia:string, dataPublicacao:string, dataUltimaLiberacao:string, dataConclusao:string, dimConvenio:obj, dimConvenio.codigo:string, dimConvenio.objeto:string, dimConvenio.numero:string, situacao:string, convenente:obj, convenente.id:integer, convenente.cpfFormatado:string, convenente.cnpjFormatado:string, convenente.numeroInscricaoSocial:string, convenente.nome:string, convenente.razaoSocialReceita:string, convenente.nomeFantasiaReceita:string, convenente.tipo:string, localidadePessoa:obj, localidadePessoa.id:integer, localidadePessoa.descricao:string, municipioConvenente:obj, municipioConvenente.codigoIBGE:string, municipioConvenente.nomeIBGE:string, municipioConvenente.codigoRegiao:string, municipioConvenente.nomeRegiao:string, municipioConvenente.pais:string, municipioConvenente.uf:obj, municipioConvenente.uf.sigla:string, municipioConvenente.uf.nome:string, orgao:obj, orgao.nome:string, orgao.codigoSIAFI:string, orgao.cnpj:string, orgao.sigla:string, orgao.descricaoPoder:string, orgao.orgaoMaximo:obj, orgao.orgaoMaximo.codigo:string, orgao.orgaoMaximo.sigla:string, orgao.orgaoMaximo.nome:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, subfuncao:obj, subfuncao.codigoSubfuncao:string, subfuncao.descricaoSubfuncap:string, subfuncao.funcao:obj, subfuncao.funcao.codigoFuncao:string, subfuncao.funcao.descricaoFuncao:string, tipoInstrumento:obj, tipoInstrumento.id:integer, tipoInstrumento.codigo:string, tipoInstrumento.descricao:string, valor:number, valorLiberado:number, valorContrapartida:number, valorDaUltimaLiberacao:number, numeroProcesso:string

### GET /api-de-dados/convenios/numero-original
Consulta um convênio do Poder Executivo Federal pelo número original do contrato — Filtros mínimos:  Página (padrão = 1);  Número;
- `numeroOriginal` (obrigatório): Número original do convênio
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ConvenioDTO): id:integer, dataReferencia:string, dataInicioVigencia:string, dataFinalVigencia:string, dataPublicacao:string, dataUltimaLiberacao:string, dataConclusao:string, dimConvenio:obj, dimConvenio.codigo:string, dimConvenio.objeto:string, dimConvenio.numero:string, situacao:string, convenente:obj, convenente.id:integer, convenente.cpfFormatado:string, convenente.cnpjFormatado:string, convenente.numeroInscricaoSocial:string, convenente.nome:string, convenente.razaoSocialReceita:string, convenente.nomeFantasiaReceita:string, convenente.tipo:string, localidadePessoa:obj, localidadePessoa.id:integer, localidadePessoa.descricao:string, municipioConvenente:obj, municipioConvenente.codigoIBGE:string, municipioConvenente.nomeIBGE:string, municipioConvenente.codigoRegiao:string, municipioConvenente.nomeRegiao:string, municipioConvenente.pais:string, municipioConvenente.uf:obj, municipioConvenente.uf.sigla:string, municipioConvenente.uf.nome:string, orgao:obj, orgao.nome:string, orgao.codigoSIAFI:string, orgao.cnpj:string, orgao.sigla:string, orgao.descricaoPoder:string, orgao.orgaoMaximo:obj, orgao.orgaoMaximo.codigo:string, orgao.orgaoMaximo.sigla:string, orgao.orgaoMaximo.nome:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, subfuncao:obj, subfuncao.codigoSubfuncao:string, subfuncao.descricaoSubfuncap:string, subfuncao.funcao:obj, subfuncao.funcao.codigoFuncao:string, subfuncao.funcao.descricaoFuncao:string, tipoInstrumento:obj, tipoInstrumento.id:integer, tipoInstrumento.codigo:string, tipoInstrumento.descricao:string, valor:number, valorLiberado:number, valorContrapartida:number, valorDaUltimaLiberacao:number, numeroProcesso:string

### GET /api-de-dados/convenios/id
Consulta um convênio do Poder Executivo Federal pelo id — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (objeto de ConvenioDTO): id:integer, dataReferencia:string, dataInicioVigencia:string, dataFinalVigencia:string, dataPublicacao:string, dataUltimaLiberacao:string, dataConclusao:string, dimConvenio:obj, dimConvenio.codigo:string, dimConvenio.objeto:string, dimConvenio.numero:string, situacao:string, convenente:obj, convenente.id:integer, convenente.cpfFormatado:string, convenente.cnpjFormatado:string, convenente.numeroInscricaoSocial:string, convenente.nome:string, convenente.razaoSocialReceita:string, convenente.nomeFantasiaReceita:string, convenente.tipo:string, localidadePessoa:obj, localidadePessoa.id:integer, localidadePessoa.descricao:string, municipioConvenente:obj, municipioConvenente.codigoIBGE:string, municipioConvenente.nomeIBGE:string, municipioConvenente.codigoRegiao:string, municipioConvenente.nomeRegiao:string, municipioConvenente.pais:string, municipioConvenente.uf:obj, municipioConvenente.uf.sigla:string, municipioConvenente.uf.nome:string, orgao:obj, orgao.nome:string, orgao.codigoSIAFI:string, orgao.cnpj:string, orgao.sigla:string, orgao.descricaoPoder:string, orgao.orgaoMaximo:obj, orgao.orgaoMaximo.codigo:string, orgao.orgaoMaximo.sigla:string, orgao.orgaoMaximo.nome:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, subfuncao:obj, subfuncao.codigoSubfuncao:string, subfuncao.descricaoSubfuncap:string, subfuncao.funcao:obj, subfuncao.funcao.codigoFuncao:string, subfuncao.funcao.descricaoFuncao:string, tipoInstrumento:obj, tipoInstrumento.id:integer, tipoInstrumento.codigo:string, tipoInstrumento.descricao:string, valor:number, valorLiberado:number, valorContrapartida:number, valorDaUltimaLiberacao:number, numeroProcesso:string

## Coronavírus

### GET /api-de-dados/coronavirus/transferencias
Consulta de transferências mensal das despesas do Poder Executivo Federal pela classificação funcional programática — Filtros mínimos:  Página (padrão = 1);  Ano do registro;  Ao menos um dos demais filtros;
- `mesAno` (obrigatório): Mês e Ano (AAAAMM)
- `codigoOrgao`: Órgão (código SIAFI)
- `tipoTransferencia`: ID do Tipo de Transferência
- `uf`: Sigla UF
- `codigoIbge`: Município
- `pagina` (obrigatório): Página consultada
- Resposta (lista de TransferenciaCoronavirusDTO): mesAno:integer, tipoTransferencia:string, codigoOrgao:string, orgao:string, tipoFavorecido:string, codigoFavorecido:string, favorecido:string, codigoFuncao:string, funcao:string, codigoPrograma:string, programa:string, codigoAcao:string, acao:string, codigoGrupoDespesa:string, grupoDespesa:string, codigoModalidadeAplicacaoDespesa:string, modalidadeAplicacaoDespesa:string, codigoElementoDespesa:string, elementoDespesa:string, valor:string

### GET /api-de-dados/coronavirus/movimento-liquido-despesa
Consulta de movimentação líquida mensal das despesas do Poder Executivo Federal pela classificação funcional programática — Filtros mínimos:  Página (padrão = 1);  Ano do registro;  Ao menos um dos demais filtros;
- `mesAnoLancamento` (obrigatório): Mês e Ano de lançamento (AAAAMM)
- `funcao`: Função (código SIAFI)
- `subfuncao`: Subfunção (código SIAFI)
- `programa`: Programa (código SIAFI)
- `acao`: Ação (código SIAFI)
- `grupoDespesa`: Grupo Despesa (código SIAFI)
- `elementoDespesa`: Elemento Despesa (código SIAFI)
- `modalidadeAplicacao`: Modalidade de Aplicação (código SIAFI)
- `idPlanoOrcamentario`: Id Plano orçamentário
- `pagina` (obrigatório): Página consultada
- Resposta (lista de MovimentacaoLiquidaCovidDTO): mesAno:integer, codigoFuncao:string, funcao:string, codigoSubfuncao:string, subfuncao:string, codigoPrograma:string, programa:string, codigoAcao:string, acao:string, idPlanoOrcamentario:integer, codigoPlanoOrcamentario:string, planoOrcamentario:string, codigoGrupoDespesa:string, grupoDespesa:string, codigoElementoDespesa:string, elementoDespesa:string, codigoModalidadeDespesa:string, modalidadeDespesa:string, empenhado:string, pago:string, liquidado:string

## Despesas Públicas

### GET /api-de-dados/despesas/tipo-transferencia
Consulta os tipos de transferências usados nas despesas — 
- Resposta (lista de IdDescricaoDTO): id:integer, descricao:string

### GET /api-de-dados/despesas/recursos-recebidos
Recebimento de recursos por favorecido — 
- `mesAnoInicio` (obrigatório): Mês ano início (MM/AAAA)
- `mesAnoFim` (obrigatório): Mês ano fim (MM/AAAA)
- `nomeFavorecido`: Nome Favorecido
- `codigoFavorecido`: CNPJ / CPF / Código do favorecido
- `tipoFavorecido`: Tipo de favorecido
- `uf`: Sigla UF
- `codigoIBGE`: Município
- `orgaoSuperior`: Órgão superior (código SIAFI)
- `orgao`: Órgão/Entidade vinculada (código SIAFI)
- `unidadeGestora`: Unidade gestora (código SIAFI)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de PessoaRecursosRecebidosUGMesDesnormalizadaDTO): anoMes:integer, codigoPessoa:string, nomePessoa:string, tipoPessoa:string, municipioPessoa:string, siglaUFPessoa:string, codigoUG:string, nomeUG:string, codigoOrgao:string, nomeOrgao:string, codigoOrgaoSuperior:string, nomeOrgaoSuperior:string, valor:number

### GET /api-de-dados/despesas/por-orgao
Consulta as despesas dos órgão do Poder Executivo Federal — Filtros mínimos:  Página (padrão = 1);  Ano do registro;  Ao menos um dos demais filtros;
- `ano` (obrigatório): Ano da despesa (AAAA)
- `orgaoSuperior`: Órgão superior (código SIAFI)
- `orgao`: Órgão/Entidade vinculada (código SIAFI)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de DespesaAnualPorOrgaoDTO): ano:integer, orgao:string, codigoOrgao:string, orgaoSuperior:string, codigoOrgaoSuperior:string, empenhado:string, liquidado:string, pago:string

### GET /api-de-dados/despesas/por-funcional-programatica
Consulta as despesas do Poder Executivo Federal pela classificação funcional programática — Filtros mínimos:  Página (padrão = 1);  Ano do registro;  Ao menos um dos demais filtros;
- `ano` (obrigatório): Ano da despesa (AAAA)
- `funcao`: Função (código SIAFI)
- `subfuncao`: Subfunção (código SIAFI)
- `programa`: Programa (código SIAFI)
- `acao`: Ação (código SIAFI)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de DespesaAnualPorFuncaoESubfuncaoDTO): ano:integer, funcao:string, codigoFuncao:string, subfuncao:string, codigoSubfuncao:string, programa:string, codigoPrograma:string, acao:string, codigoAcao:string, empenhado:string, liquidado:string, pago:string

### GET /api-de-dados/despesas/por-funcional-programatica/movimentacao-liquida
Consulta de movimentação líquida anual das despesas do Poder Executivo Federal pela classificação funcional programática — Filtros mínimos:  Página (padrão = 1);  Ano do registro;  Ao menos um dos demais filtros;
- `ano` (obrigatório): Ano da despesa (AAAA)
- `funcao`: Função (código SIAFI)
- `subfuncao`: Subfunção (código SIAFI)
- `programa`: Programa (código SIAFI)
- `acao`: Ação (código SIAFI)
- `grupoDespesa`: Grupo Despesa (código SIAFI)
- `elementoDespesa`: Elemento Despesa (código SIAFI)
- `modalidadeAplicacao`: Modalidade de Aplicação (código SIAFI)
- `idPlanoOrcamentario`: Id Plano orçamentário
- `pagina` (obrigatório): Página consultada
- Resposta (lista de DespesaLiquidaAnualPorFuncaoESubfuncaoDTO): ano:integer, funcao:string, codigoFuncao:string, subfuncao:string, codigoSubfuncao:string, programa:string, codigoPrograma:string, acao:string, codigoAcao:string, planoOrcamentario:string, idPlanoOrcamentario:integer, codigoPlanoOrcamentario:string, grupoDespesa:string, codigoGrupoDespesa:string, elementoDespesa:string, codigoElementoDespesa:string, modalidadeDespesa:string, codigoModalidadeDespesa:string, empenhado:string, liquidado:string, pago:string

### GET /api-de-dados/despesas/plano-orcamentario
Consulta Plano orçamentário — 
- `codPlanoOrcamentario`: Código Plano Orçamentária
- `descPlanoOrcamentario`: Descrição Plano Orçamentário
- `codPOIdentfAcompanhamento`: Identificado de acompanhamento
- `ano` (obrigatório): Ano
- `pagina` (obrigatório): Página consultada
- Resposta (lista de DespesasPorPlanoOrcamentarioDTO): id:integer, codigo:string, descricao:string, codUnidadeOrcamentaria:string, codigoFuncao:string, codigoSubFuncao:string, codigoPrograma:string, codigoAcao:string, codPOIdAcompanhamento:string, descPOIdAcompanhamento:string, numAno:integer

### GET /api-de-dados/despesas/itens-de-empenho
Consulta os itens de um Empenho — 
- `codigoDocumento` (obrigatório): Código do empenho (Unidade Gestora + Gestão + Número do documento)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de DetalhamentoDoGastoDTO): codigoItemEmpenho:string, descricao:string, codigoSubelemento:string, descricaoSubelemento:string, valorAtual:string, sequencial:integer

### GET /api-de-dados/despesas/itens-de-empenho/historico
Consulta o histórico de um item de empenho — 
- `codigoDocumento` (obrigatório): Código do empenho (Unidade Gestora + Gestão + Número do documento)
- `sequencial` (obrigatório): Número sequencial do item de empenho
- `pagina` (obrigatório): Página consultada
- Resposta (lista de HistoricoSubItemEmpenhoDTO): data:string, operacao:string, quantidade:string, valorUnitario:string, valorTotal:string

### GET /api-de-dados/despesas/favorecidos-finais-por-documento
Consulta favorecidos finais por documento — Filtros mínimos: Código do registro
- `codigoDocumento` (obrigatório): Código do documento (Unidade Gestora + Gestão + Número do documento)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ConsultaFavorecidosFinaisPorDocumentoDTO): skFatDW:integer, codigoPagamento:string, codigoListaCredor:string, valorFinal:string, tipoOB:string, tipoDocumento:string, dataCarga:string, skPessoaFinal:integer, codigoFavorecidoFinal:string, nomeFavorecidoFinal:string, tipoFavorecidoFinal:string, ufFavorecidoFinal:string, municipioFavorecidoFinal:string, skPessoaDespesa:integer, codigoFavorecidoDespesa:string, nomeFavorecidoDespesa:string, tipoFavorecidoDespesa:string, codigoOrgaoSuperior:string, orgaoSuperior:string, codigoOrgaoVinculado:string, orgaoVinculado:string, codigoUnidadeGestora:string, unidadeGestora:string

### GET /api-de-dados/despesas/empenhos-impactados
Consulta empenhos impactados por documento/fase — Filtros mínimos: Código do registro e fase da despesa (liquidação ou pagamento somente)
- `codigoDocumento` (obrigatório): Código do documento (Unidade Gestora + Gestão + Número do documento)
- `fase` (obrigatório): Fase da despesa (2 - Liquidação, 3 - Pagamento)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de EmpenhoImpactadoBasicoDTO): empenho:string, subitem:string, empenhoResumido:string, valorLiquidado:string, valorPago:string, valorRestoInscrito:string, valorRestoCancelado:string, valorRestoPago:string

### GET /api-de-dados/despesas/documentos
Consulta todos os documentos de despesas — Filtros mínimos:  Página (padrão = 1);  Período de no máximo 1 dia;  Fase da despesa;  Ao menos um dos demais filtros;
- `unidadeGestora`: Unidade gestora emitente (código SIAFI)
- `gestao`: Gestão (código SIAFI)
- `dataEmissao` (obrigatório): Data de emissão (DD/MM/AAAA)
- `fase` (obrigatório): Fase da despesa (1 - Empenho, 2 - Liquidação, 3 - Pagamento)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de DespesasPorDocumentoDTO): data:string, documento:string, documentoResumido:string, observacao:string, funcao:string, subfuncao:string, programa:string, acao:string, subTitulo:string, localizadorGasto:string, fase:string, especie:string, favorecido:string, codigoFavorecido:string, nomeFavorecido:string, ufFavorecido:string, valor:string, codigoUg:string, ug:string, codigoUo:string, uo:string, codigoOrgao:string, orgao:string, codigoOrgaoSuperior:string, orgaoSuperior:string, categoria:string, grupo:string, elemento:string, modalidade:string, numeroProcesso:string, planoOrcamentario:string, autor:string, favorecidoIntermediario:boolean, favorecidoListaFaturas:boolean

### GET /api-de-dados/despesas/documentos/{codigo}
Consulta um documento pelo código (Unidade Gestora + Gestão + Número do documento) — Filtros mínimos: Código do registro
- `codigo` (obrigatório): Código do registro
- Resposta (objeto de DespesasPorDocumentoDTO): data:string, documento:string, documentoResumido:string, observacao:string, funcao:string, subfuncao:string, programa:string, acao:string, subTitulo:string, localizadorGasto:string, fase:string, especie:string, favorecido:string, codigoFavorecido:string, nomeFavorecido:string, ufFavorecido:string, valor:string, codigoUg:string, ug:string, codigoUo:string, uo:string, codigoOrgao:string, orgao:string, codigoOrgaoSuperior:string, orgaoSuperior:string, categoria:string, grupo:string, elemento:string, modalidade:string, numeroProcesso:string, planoOrcamentario:string, autor:string, favorecidoIntermediario:boolean, favorecidoListaFaturas:boolean

### GET /api-de-dados/despesas/documentos-relacionados
Consulta os documentos relacionados a um Empenho, Liquidação ou Pagamento — 
- `codigoDocumento` (obrigatório): Código do documento (Unidade Gestora + Gestão + Número do documento)
- `fase` (obrigatório): Fase da despesa (1 - Empenho, 2 - Liquidação, 3 - Pagamento)
- Resposta (lista de DocumentoRelacionadoDTO): data:string, fase:string, documento:string, documentoResumido:string, especie:string, orgaoSuperior:string, orgaoVinculado:string, unidadeGestora:string, elementoDespesa:string, favorecido:string, valor:string

### GET /api-de-dados/despesas/documentos-por-favorecido
Consulta Empenhos, Liquidações e Pagamentos emitidos para um favorecido — A informação favorecidoIntermediario indica se o documento foi emitido para o favorecido ou se ele é apenas um intermediário que recebe o recurso e repassa-o para os favorecidos finais
- `codigoPessoa` (obrigatório): Código do Favorecido (CPF, CNPJ ou código do SIAFI)
- `fase` (obrigatório): Fase da despesa (1 - Empenho, 2 - Liquidação, 3 - Pagamento)
- `ano` (obrigatório): Ano de emissão do documento
- `ug`: Código da unidade gestora emissora do documento
- `gestao`: Código da gestão do documento
- `ordenacaoResultado`: Ordenação de Resultado (1 - Valor Ascendente, 2 - Valor Descendente, 3 - Data Ascendente, 4 - Data Descendente)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de DespesasPorDocumentoDTO): data:string, documento:string, documentoResumido:string, observacao:string, funcao:string, subfuncao:string, programa:string, acao:string, subTitulo:string, localizadorGasto:string, fase:string, especie:string, favorecido:string, codigoFavorecido:string, nomeFavorecido:string, ufFavorecido:string, valor:string, codigoUg:string, ug:string, codigoUo:string, uo:string, codigoOrgao:string, orgao:string, codigoOrgaoSuperior:string, orgaoSuperior:string, categoria:string, grupo:string, elemento:string, modalidade:string, numeroProcesso:string, planoOrcamentario:string, autor:string, favorecidoIntermediario:boolean, favorecidoListaFaturas:boolean

## Emendas parlamentares

### GET /api-de-dados/emendas
Consulta as emendas parlamentares — Filtros mínimos:  Página (padrão = 1);
- `codigoEmenda`: Código da Emenda
- `numeroEmenda`: Número da emenda
- `nomeAutor`: Nome do Autor
- `tipoEmenda`: Tipo de emenda
- `ano`: Ano
- `codigoFuncao`: Código da função
- `codigoSubfuncao`: Código da subfunção
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ConsultaEmendasDTO): codigoEmenda:string, ano:integer, tipoEmenda:string, autor:string, nomeAutor:string, numeroEmenda:string, localidadeDoGasto:string, funcao:string, subfuncao:string, valorEmpenhado:string, valorLiquidado:string, valorPago:string, valorRestoInscrito:string, valorRestoCancelado:string, valorRestoPago:string

### GET /api-de-dados/emendas/documentos/{codigo}
Consulta os documentos relacionados à emenda parlamentar pelo código da emenda — Filtros mínimos:  Página (padrão = 1);
- `codigo` (obrigatório): Código da emenda
- `pagina` (obrigatório): Página consultada
- Resposta (lista de DocumentoRelacionadoEmendaDTO): id:integer, data:string, fase:string, codigoDocumento:string, codigoDocumentoResumido:string, especieTipo:string, tipoEmenda:string

## Gastos por meio de cartão de pagamento

### GET /api-de-dados/cartoes
Consulta os registros de Cartões de Pagamento — Filtros mínimos:  Página (padrão = 1);  Período de até 12 meses ou um órgão ou um portador ou um favorecido específico;
- `mesExtratoInicio`: Mês extrato início (MM/AAAA)
- `mesExtratoFim`: Mês extrato fim (MM/AAAA)
- `dataTransacaoInicio`: Data transação início (DD/MM/AAAA)
- `dataTransacaoFim`: Data transação fim (DD/MM/AAAA)
- `tipoCartao`: Tipo de cartão (CPGF=1 ou CPCC=2 ou CPDC=3)
- `codigoOrgao`: Órgão/Entidade (Código SIAFI)
- `cpfPortador`: Portador (CPF)
- `cpfCnpjFavorecido`: Favorecido (CPF/CNPJ)
- `valorDe`: Valor de (####,##)
- `valorAte`: Valor até (####,##)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de CartoesDTO): id:integer, mesExtrato:string, dataTransacao:string, valorTransacao:string, tipoCartao:obj, tipoCartao.id:integer, tipoCartao.codigo:string, tipoCartao.descricao:string, estabelecimento:obj, estabelecimento.id:integer, estabelecimento.cpfFormatado:string, estabelecimento.cnpjFormatado:string, estabelecimento.numeroInscricaoSocial:string, estabelecimento.nome:string, estabelecimento.razaoSocialReceita:string, estabelecimento.nomeFantasiaReceita:string, estabelecimento.tipo:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, portador:obj, portador.cpfFormatado:string, portador.nis:string, portador.nome:string

## Imóveis Funcionais

### GET /api-de-dados/situacao-imovel
Consulta situações dos imóveis funcionais — 

### GET /api-de-dados/permissionarios
Consulta relação de ocupantes — Filtros mínimos:  Página (padrão = 1);
- `codigoOrgaoResponsavelGestaoSiafi`: Código do Órgão Responsável pela Gestão(SIAFI)
- `descricaoOrgaoOcupante`: Descrição do Órgão do Ocupante
- `cpfOcupante`: CPF Ocupante
- `dataInicioOcupacao`: Data início ocupação(DD/MM/AAAA)
- `dataFimOcupacao`: Data fim ocupação (DD/MM/AAAA)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de PermissionarioDTO): id:integer, dataReferencia:string, orgaoResponsavel:obj, orgaoResponsavel.nome:string, orgaoResponsavel.codigoSIAFI:string, dataInicioOcupacao:string, pessoaPermissionario:obj, pessoaPermissionario.id:integer, pessoaPermissionario.cpfFormatado:string, pessoaPermissionario.cnpjFormatado:string, pessoaPermissionario.numeroInscricaoSocial:string, pessoaPermissionario.nome:string, pessoaPermissionario.razaoSocialReceita:string, pessoaPermissionario.nomeFantasiaReceita:string, pessoaPermissionario.tipo:string, permissionario:obj, permissionario.cpfFormatado:string, permissionario.nis:string, permissionario.nome:string, orgaoPermissionario:string, cargo:string, valorPagoMes:number

### GET /api-de-dados/imoveis
Consulta relação de imóveis — Filtros mínimos:  Página (padrão = 1);
- `codigoOrgaoSiafiResponsavelGestao`: Código do Órgão (SIAFI)
- `situacao`: Situação Imóvel
- `regiao`: Região
- `cep`: CEP
- `endereco`: Endereço
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ImovelFuncionalDTO): id:integer, dataReferencia:string, orgaoResponsavel:obj, orgaoResponsavel.nome:string, orgaoResponsavel.codigoSIAFI:string, situacao:obj, situacao.id:integer, situacao.descricao:string, regiao:obj, regiao.id:integer, regiao.descricao:string, endereco:string, cep:string

## Licitações do Poder Executivo Federal

### GET /api-de-dados/licitacoes
Consulta todas as licitações do Poder Executivo Federal — Filtros mínimos:  Página (padrão = 1);  Período de no máximo 1 mês; Código do Órgão (SIAFI)
- `dataInicial`: Data de abertura inicial (DD/MM/AAAA)
- `dataFinal`: Data de abertura final (DD/MM/AAAA)
- `codigoOrgao` (obrigatório): Código do Órgão (SIAFI)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de LicitacaoDTO): id:integer, licitacao:obj, licitacao.numero:string, licitacao.objeto:string, licitacao.numeroProcesso:string, licitacao.contatoResponsavel:string, dataResultadoCompra:string, dataAbertura:string, dataReferencia:string, dataPublicacao:string, situacaoCompra:string, modalidadeLicitacao:string, instrumentoLegal:string, valor:number, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string

### GET /api-de-dados/licitacoes/{id}
Consulta uma licitação do Poder Executivo Federal pelo id — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (objeto de LicitacaoDTO): id:integer, licitacao:obj, licitacao.numero:string, licitacao.objeto:string, licitacao.numeroProcesso:string, licitacao.contatoResponsavel:string, dataResultadoCompra:string, dataAbertura:string, dataReferencia:string, dataPublicacao:string, situacaoCompra:string, modalidadeLicitacao:string, instrumentoLegal:string, valor:number, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string

### GET /api-de-dados/licitacoes/ugs
Consulta as Unidades Gestoras que realizaram licitações — 
- `pagina` (obrigatório): Página consultada
- Resposta (lista de UnidadeGestoraDTO): codigo:string, nome:string, descricaoPoder:string, orgaoVinculado:obj, orgaoVinculado.codigoSIAFI:string, orgaoVinculado.cnpj:string, orgaoVinculado.sigla:string, orgaoVinculado.nome:string, orgaoMaximo:obj, orgaoMaximo.codigo:string, orgaoMaximo.sigla:string, orgaoMaximo.nome:string

### GET /api-de-dados/licitacoes/por-ug-modalidade-numero
Consulta uma licitação pelo código da Unidade Gestora, número e modalidade — O número da licitação deve conter somente números, por exemplo, para a licitação 2/2020 o parâmetro deve ter o valor 22020
- `codigoUG` (obrigatório): Código da Unidade Gestora
- `numero` (obrigatório): Número da Licitação (NNNNNAAAA)
- `codigoModalidade` (obrigatório): Código da Modalidade da Licitação
- Resposta (lista de LicitacaoDTO): id:integer, licitacao:obj, licitacao.numero:string, licitacao.objeto:string, licitacao.numeroProcesso:string, licitacao.contatoResponsavel:string, dataResultadoCompra:string, dataAbertura:string, dataReferencia:string, dataPublicacao:string, situacaoCompra:string, modalidadeLicitacao:string, instrumentoLegal:string, valor:number, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string

### GET /api-de-dados/licitacoes/por-processo
Consulta uma licitação pelo número do processo — O número do processo deve conter somente números
- `processo` (obrigatório): Número do Processo
- Resposta (lista de LicitacaoDTO): id:integer, licitacao:obj, licitacao.numero:string, licitacao.objeto:string, licitacao.numeroProcesso:string, licitacao.contatoResponsavel:string, dataResultadoCompra:string, dataAbertura:string, dataReferencia:string, dataPublicacao:string, situacaoCompra:string, modalidadeLicitacao:string, instrumentoLegal:string, valor:number, municipio:obj, municipio.codigoIBGE:string, municipio.nomeIBGE:string, municipio.codigoRegiao:string, municipio.nomeRegiao:string, municipio.pais:string, municipio.uf:obj, municipio.uf.sigla:string, municipio.uf.nome:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string

### GET /api-de-dados/licitacoes/participantes
Consulta os participantes de uma licitação — O número da licitação deve conter somente números, por exemplo, para a licitação 2/2020 o parâmetro deve ter o valor 22020
- `codigoUG` (obrigatório): Código da Unidade Gestora
- `numero` (obrigatório): Número da Licitação (NNNNNAAAA)
- `codigoModalidade` (obrigatório): Código da Modalidade da Licitação
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ParticipanteLicitacaoDTO): tipoParticipante:string, idParticipante:string, cpfCnpj:string, nome:string

### GET /api-de-dados/licitacoes/modalidades
Consulta as modalidades de licitação — 
- Resposta (lista de CodigoDescricaoDTO): codigo:string, descricao:string

### GET /api-de-dados/licitacoes/itens-licitados
Consulta os itens licitados pelo id licitação — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ItemLicitacaoDTO): codigoItemCompra:string, numero:string, descricao:string, quantidade:integer, valor:string, cpfCnpjVencedor:string, tipoPessoa:string, idVencedor:string, nome:string, descComplementarItemCompra:string, descUnidadeFornecimento:string

### GET /api-de-dados/licitacoes/empenhos
Consulta os empenhos de uma licitação — O número da licitação deve conter somente números, por exemplo, para a licitação 2/2020 o parâmetro deve ter o valor 22020
- `codigoUG` (obrigatório): Código da Unidade Gestora
- `numero` (obrigatório): Número da Licitação (NNNNNAAAA)
- `codigoModalidade` (obrigatório): Código da Modalidade da Licitação
- `pagina` (obrigatório): Página consultada
- Resposta (lista de EmpenhoComprasDTO): empenho:string, empenhoResumido:string, dataEmissao:string, observacao:string, valor:string

### GET /api-de-dados/licitacoes/contratos-relacionados-licitacao
Consulta os contratos relacionados a licitação — Filtros mínimos: ID do registro
- `codigoUG` (obrigatório): Código da Unidade Gestora
- `numero` (obrigatório): Número da Licitação (NNNNNAAAA)
- `codigoModalidade` (obrigatório): Código da Modalidade da Licitação
- Resposta (lista de ContratoDTO): id:integer, numero:string, objeto:string, numeroProcesso:string, fundamentoLegal:string, compra:obj, compra.numero:string, compra.objeto:string, compra.numeroProcesso:string, compra.contatoResponsavel:string, situacaoContrato:string, modalidadeCompra:string, unidadeGestora:obj, unidadeGestora.codigo:string, unidadeGestora.nome:string, unidadeGestora.descricaoPoder:string, unidadeGestora.orgaoVinculado:obj, unidadeGestora.orgaoVinculado.codigoSIAFI:string, unidadeGestora.orgaoVinculado.cnpj:string, unidadeGestora.orgaoVinculado.sigla:string, unidadeGestora.orgaoVinculado.nome:string, unidadeGestora.orgaoMaximo:obj, unidadeGestora.orgaoMaximo.codigo:string, unidadeGestora.orgaoMaximo.sigla:string, unidadeGestora.orgaoMaximo.nome:string, unidadeGestoraCompras:obj, unidadeGestoraCompras.codigo:string, unidadeGestoraCompras.nome:string, unidadeGestoraCompras.descricaoPoder:string, unidadeGestoraCompras.orgaoVinculado:obj, unidadeGestoraCompras.orgaoVinculado.codigoSIAFI:string, unidadeGestoraCompras.orgaoVinculado.cnpj:string, unidadeGestoraCompras.orgaoVinculado.sigla:string, unidadeGestoraCompras.orgaoVinculado.nome:string, unidadeGestoraCompras.orgaoMaximo:obj, unidadeGestoraCompras.orgaoMaximo.codigo:string, unidadeGestoraCompras.orgaoMaximo.sigla:string, unidadeGestoraCompras.orgaoMaximo.nome:string, dataAssinatura:string, dataPublicacaoDOU:string, dataInicioVigencia:string, dataFimVigencia:string, fornecedor:obj, fornecedor.id:integer, fornecedor.cpfFormatado:string, fornecedor.cnpjFormatado:string, fornecedor.numeroInscricaoSocial:string, fornecedor.nome:string, fornecedor.razaoSocialReceita:string, fornecedor.nomeFantasiaReceita:string, fornecedor.tipo:string, valorInicialCompra:number, valorFinalCompra:number

## Notas Fiscais

### GET /api-de-dados/notas-fiscais
Consulta todas as notas fiscais eletrônicas (NFe´s) do Poder Executivo Federal — Filtros mínimos:  Página (padrão = 1);  CNPJ Emitente / Órgão / Produto;
- `cnpjEmitente`: CNPJ do emitente
- `codigoOrgao`: Código do Órgão (SIAFI)
- `nomeProduto`: Nome do produto
- `pagina` (obrigatório): Página consultada
- Resposta (lista de NotaFiscalDTO): id:integer, codigoOrgaoSuperiorDestinatario:string, orgaoSuperiorDestinatario:string, codigoOrgaoDestinatario:string, orgaoDestinatario:string, nomeFornecedor:string, cnpjFornecedor:string, municipioFornecedor:string, chaveNotaFiscal:string, valorNotaFiscal:string, tipoEventoMaisRecente:string, dataTipoEventoMaisRecente:string, dataEmissao:string, numero:integer, serie:integer

### GET /api-de-dados/notas-fiscais-por-chave
Consulta uma nota fiscal eletrônica (NFe) do Poder Executivo Federal pela chave única — Filtros mínimos: Código do registro
- `chaveUnicaNotaFiscal` (obrigatório): Chave única da nota fiscal
- Resposta (objeto de DetalheNotaFiscalDTO): notaFiscalDTO:obj, notaFiscalDTO.id:integer, notaFiscalDTO.codigoOrgaoSuperiorDestinatario:string, notaFiscalDTO.orgaoSuperiorDestinatario:string, notaFiscalDTO.codigoOrgaoDestinatario:string, notaFiscalDTO.orgaoDestinatario:string, notaFiscalDTO.nomeFornecedor:string, notaFiscalDTO.cnpjFornecedor:string, notaFiscalDTO.municipioFornecedor:string, notaFiscalDTO.chaveNotaFiscal:string, notaFiscalDTO.valorNotaFiscal:string, notaFiscalDTO.tipoEventoMaisRecente:string, notaFiscalDTO.dataTipoEventoMaisRecente:string, notaFiscalDTO.dataEmissao:string, notaFiscalDTO.numero:integer, notaFiscalDTO.serie:integer, itensNotaFiscal:array, itensNotaFiscal.numeroProduto:string, itensNotaFiscal.descricaoProdutoServico:string, itensNotaFiscal.codigoNcmSh:string, itensNotaFiscal.ncmSh:string, itensNotaFiscal.cfop:string, itensNotaFiscal.quantidade:string, itensNotaFiscal.unidade:string, itensNotaFiscal.valorUnitario:string, itensNotaFiscal.valor:string, eventosNotaFiscal:array, eventosNotaFiscal.dataEvento:string, eventosNotaFiscal.tipoEvento:string, eventosNotaFiscal.evento:string, eventosNotaFiscal.motivo:string

## Pessoas físicas e jurídicas

### GET /api-de-dados/pessoa-juridica
Consulta os registros de Pessoas Jurídicas — 
- `cnpj` (obrigatório): CNPJ
- Resposta (objeto de PessoaJuridicaDTO): cnpj:string, razaoSocial:string, nomeFantasia:string, favorecidoDespesas:boolean, possuiContratacao:boolean, convenios:boolean, favorecidoTransferencias:boolean, sancionadoCEPIM:boolean, sancionadoCEIS:boolean, sancionadoCNEP:boolean, sancionadoCEAF:boolean, participanteLicitacao:boolean, emitiuNFe:boolean, beneficiadoRenunciaFiscal:boolean, isentoImuneRenunciaFiscal:boolean, habilitadoRenunciaFiscal:boolean

### GET /api-de-dados/pessoa-fisica
Consulta os registros de Pessoas Físicas — Filtros mínimos: CPF ou NIS
- `cpf`: CPF
- `nis`: NIS
- Resposta (objeto de PessoaFisicaDTO): cpf:string, nome:string, nis:string, favorecidoDespesas:boolean, servidor:boolean, beneficiarioDiarias:boolean, permissionario:boolean, contratado:boolean, sancionadoCEIS:boolean, sancionadoCNEP:boolean, sancionadoCEAF:boolean, portadorCPDC:boolean, portadorCPGF:boolean, favorecidoBolsaFamilia:boolean, favorecidoPeti:boolean, favorecidoSafra:boolean, favorecidoSeguroDefeso:boolean, favorecidoBpc:boolean, favorecidoTransferencias:boolean, favorecidoCPCC:boolean, favorecidoCPDC:boolean, favorecidoCPGF:boolean, participanteLicitacao:boolean, servidorInativo:boolean, pensionistaOuRepresentanteLegal:boolean, instituidorPensao:boolean, auxilioEmergencial:boolean, favorecidoAuxilioBrasil:boolean, favorecidoNovoBolsaFamilia:boolean, favorecidoAuxilioReconstrucao:boolean

## Renúncias Fiscais

### GET /api-de-dados/renuncias-valor
Consulta de Valores Renunciados — 
- `nomeSiglaUF`: Nome ou Sigla UF
- `codigoIbge`: Código IBGE
- `cnpj`: CNPJ
- `pagina` (obrigatório): Página consultada
- Resposta (lista de RenunciaDTO): ano:integer, valorRenunciado:number, tipoRenuncia:string, descricaoBeneficioFiscal:string, descricaoFundamentoLegal:string, tributo:string, formaTributacao:string, cnpj:string, razaoSocial:string, nomeFantasia:string, cnaeCodigoGrupo:string, cnaeCodigoClasse:string, cnaeCodigoSubClasse:string, cnaeNomeClasse:string, cnaeDivisao:string, uf:string, municipio:string, codigoIBGE:string

### GET /api-de-dados/renuncias-fiscais-empresas-imunes-isentas
Consulta Pessoas Jurídicas Imunes e Isentas — 
- `nomeSiglaUF`: Nome ou Sigla UF
- `codigoIbge`: Código IBGE
- `cnpj`: CNPJ
- `beneficiarioNomeFantasia`: Beneficiário/Nome Fantasia
- `pagina` (obrigatório): Página consultada
- Resposta (lista de EmpresaImuneIsentaDTO): cnpj:string, beneficiario:string, nomeFantasia:string, uf:string, codigoIBGEMunicipio:string, municipio:string, cnaeCodigoGrupo:string, cnaeCodigoClasse:string, cnaeCodigoSubClasse:string, cnaeNomeClasse:string, cnaeDivisao:string, tipoEntidade:string, beneficioFiscal:string

### GET /api-de-dados/renuncias-fiscais-empresas-habilitadas-beneficios-fiscais
Consulta Pessoas Jurídicas Habilitadas a Benefício Fiscal — 
- `nomeSiglaUF`: Nome ou Sigla UF
- `codigoIbge`: Código IBGE
- `cnpj`: CNPJ
- `beneficiarioNomeFantasia`: Beneficiário/Nome Fantasia
- `pagina` (obrigatório): Página consultada
- Resposta (lista de EmpresaHabilitadaBeneficioFiscalDTO): fruicaoVigente:string, dataInicioFruicao:string, dataFimFruicao:string, cnpj:string, beneficiario:string, nomeFantasia:string, uf:string, codigoIBGEMunicipio:string, municipio:string, cnaeCodigoGrupo:string, cnaeCodigoClasse:string, cnaeCodigoSubClasse:string, cnaeNomeClasse:string, cnaeDivisao:string, beneficioFiscal:string, descricao:string, fundamentoLegal:string

## Sanções

### GET /api-de-dados/cnep
Consulta os registros do CNEP por CNPJ ou CPF Sancionado/Órgão Sancionador/Período — Filtros mínimos:  Página (padrão = 1);
- `codigoSancionado`: CNPJ ou CPF do Sancionado
- `nomeSancionado`: Nome, nome fantasia ou razão social do Sancionado
- `orgaoSancionador`: Órgão Sancionador
- `dataInicialSancao`: Data Inicial da Sanção (DD/MM/AAAA)
- `dataFinalSancao`: Data Final da Sanção (DD/MM/AAAA)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de CnepDTO): id:integer, dataReferencia:string, dataInicioSancao:string, dataFimSancao:string, dataPublicacaoSancao:string, dataTransitadoJulgado:string, dataOrigemInformacao:string, tipoSancao:obj, tipoSancao.descricaoResumida:string, tipoSancao.descricaoPortal:string, fonteSancao:obj, fonteSancao.nomeExibicao:string, fonteSancao.telefoneContato:string, fonteSancao.enderecoContato:string, fundamentacao:array, fundamentacao.codigo:string, fundamentacao.descricao:string, orgaoSancionador:obj, orgaoSancionador.nome:string, orgaoSancionador.siglaUf:string, orgaoSancionador.poder:string, orgaoSancionador.esfera:string, sancionado:obj, sancionado.nome:string, sancionado.codigoFormatado:string, valorMulta:string, pessoa:obj, pessoa.id:integer, pessoa.cpfFormatado:string, pessoa.cnpjFormatado:string, pessoa.numeroInscricaoSocial:string, pessoa.nome:string, pessoa.razaoSocialReceita:string, pessoa.nomeFantasiaReceita:string, pessoa.tipo:string, textoPublicacao:string, linkPublicacao:string, detalhamentoPublicacao:string, numeroProcesso:string, abrangenciaDefinidaDecisaoJudicial:string, informacoesAdicionaisDoOrgaoSancionador:string

### GET /api-de-dados/cnep/{id}
Consulta um registro do CNEP pelo id — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (objeto de CnepDTO): id:integer, dataReferencia:string, dataInicioSancao:string, dataFimSancao:string, dataPublicacaoSancao:string, dataTransitadoJulgado:string, dataOrigemInformacao:string, tipoSancao:obj, tipoSancao.descricaoResumida:string, tipoSancao.descricaoPortal:string, fonteSancao:obj, fonteSancao.nomeExibicao:string, fonteSancao.telefoneContato:string, fonteSancao.enderecoContato:string, fundamentacao:array, fundamentacao.codigo:string, fundamentacao.descricao:string, orgaoSancionador:obj, orgaoSancionador.nome:string, orgaoSancionador.siglaUf:string, orgaoSancionador.poder:string, orgaoSancionador.esfera:string, sancionado:obj, sancionado.nome:string, sancionado.codigoFormatado:string, valorMulta:string, pessoa:obj, pessoa.id:integer, pessoa.cpfFormatado:string, pessoa.cnpjFormatado:string, pessoa.numeroInscricaoSocial:string, pessoa.nome:string, pessoa.razaoSocialReceita:string, pessoa.nomeFantasiaReceita:string, pessoa.tipo:string, textoPublicacao:string, linkPublicacao:string, detalhamentoPublicacao:string, numeroProcesso:string, abrangenciaDefinidaDecisaoJudicial:string, informacoesAdicionaisDoOrgaoSancionador:string

### GET /api-de-dados/cepim
Consulta os registros do CEPIM por CNPJ ou CPF Sancionado/Órgão superior — Filtros mínimos:  Página (padrão = 1);
- `cnpjSancionado`: CNPJ do Sancionado
- `nomeSancionado`: Nome, nome fantasia ou razão social do Sancionado
- `ufSancionado`: UF do Sancionado (sigla)
- `orgaoEntidade`: Órgão/Entidade
- `pagina` (obrigatório): Página consultada
- Resposta (lista de CepimDTO): id:integer, dataReferencia:string, motivo:string, orgaoSuperior:obj, orgaoSuperior.nome:string, orgaoSuperior.codigoSIAFI:string, orgaoSuperior.cnpj:string, orgaoSuperior.sigla:string, orgaoSuperior.descricaoPoder:string, orgaoSuperior.orgaoMaximo:obj, orgaoSuperior.orgaoMaximo.codigo:string, orgaoSuperior.orgaoMaximo.sigla:string, orgaoSuperior.orgaoMaximo.nome:string, pessoaJuridica:obj, pessoaJuridica.id:integer, pessoaJuridica.cpfFormatado:string, pessoaJuridica.cnpjFormatado:string, pessoaJuridica.numeroInscricaoSocial:string, pessoaJuridica.nome:string, pessoaJuridica.razaoSocialReceita:string, pessoaJuridica.nomeFantasiaReceita:string, pessoaJuridica.tipo:string, convenio:obj, convenio.codigo:string, convenio.objeto:string, convenio.numero:string

### GET /api-de-dados/cepim/{id}
Consulta um registro do CEPIM pelo id — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (objeto de CepimDTO): id:integer, dataReferencia:string, motivo:string, orgaoSuperior:obj, orgaoSuperior.nome:string, orgaoSuperior.codigoSIAFI:string, orgaoSuperior.cnpj:string, orgaoSuperior.sigla:string, orgaoSuperior.descricaoPoder:string, orgaoSuperior.orgaoMaximo:obj, orgaoSuperior.orgaoMaximo.codigo:string, orgaoSuperior.orgaoMaximo.sigla:string, orgaoSuperior.orgaoMaximo.nome:string, pessoaJuridica:obj, pessoaJuridica.id:integer, pessoaJuridica.cpfFormatado:string, pessoaJuridica.cnpjFormatado:string, pessoaJuridica.numeroInscricaoSocial:string, pessoaJuridica.nome:string, pessoaJuridica.razaoSocialReceita:string, pessoaJuridica.nomeFantasiaReceita:string, pessoaJuridica.tipo:string, convenio:obj, convenio.codigo:string, convenio.objeto:string, convenio.numero:string

### GET /api-de-dados/ceis
Consulta os registros do CEIS por CNPJ ou CPF Sancionado/Órgão Sancionador/Período — Filtros mínimos:  Página (padrão = 1);
- `codigoSancionado`: CNPJ ou CPF Sancionado
- `nomeSancionado`: Nome, nome fantasia ou razão social do Sancionado
- `orgaoSancionador`: Órgão Sancionador
- `dataInicialSancao`: Data Inicial da Sanção (DD/MM/AAAA)
- `dataFinalSancao`: Data Final da Sanção (DD/MM/AAAA)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de CeisDTO): id:integer, dataReferencia:string, dataInicioSancao:string, dataFimSancao:string, dataPublicacaoSancao:string, dataTransitadoJulgado:string, dataOrigemInformacao:string, tipoSancao:obj, tipoSancao.descricaoResumida:string, tipoSancao.descricaoPortal:string, fonteSancao:obj, fonteSancao.nomeExibicao:string, fonteSancao.telefoneContato:string, fonteSancao.enderecoContato:string, fundamentacao:array, fundamentacao.codigo:string, fundamentacao.descricao:string, orgaoSancionador:obj, orgaoSancionador.nome:string, orgaoSancionador.siglaUf:string, orgaoSancionador.poder:string, orgaoSancionador.esfera:string, sancionado:obj, sancionado.nome:string, sancionado.codigoFormatado:string, pessoa:obj, pessoa.id:integer, pessoa.cpfFormatado:string, pessoa.cnpjFormatado:string, pessoa.numeroInscricaoSocial:string, pessoa.nome:string, pessoa.razaoSocialReceita:string, pessoa.nomeFantasiaReceita:string, pessoa.tipo:string, textoPublicacao:string, linkPublicacao:string, detalhamentoPublicacao:string, numeroProcesso:string, abrangenciaDefinidaDecisaoJudicial:string, informacoesAdicionaisDoOrgaoSancionador:string

### GET /api-de-dados/ceis/{id}
Consulta um registro do CEIS pelo id — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (objeto de CeisDTO): id:integer, dataReferencia:string, dataInicioSancao:string, dataFimSancao:string, dataPublicacaoSancao:string, dataTransitadoJulgado:string, dataOrigemInformacao:string, tipoSancao:obj, tipoSancao.descricaoResumida:string, tipoSancao.descricaoPortal:string, fonteSancao:obj, fonteSancao.nomeExibicao:string, fonteSancao.telefoneContato:string, fonteSancao.enderecoContato:string, fundamentacao:array, fundamentacao.codigo:string, fundamentacao.descricao:string, orgaoSancionador:obj, orgaoSancionador.nome:string, orgaoSancionador.siglaUf:string, orgaoSancionador.poder:string, orgaoSancionador.esfera:string, sancionado:obj, sancionado.nome:string, sancionado.codigoFormatado:string, pessoa:obj, pessoa.id:integer, pessoa.cpfFormatado:string, pessoa.cnpjFormatado:string, pessoa.numeroInscricaoSocial:string, pessoa.nome:string, pessoa.razaoSocialReceita:string, pessoa.nomeFantasiaReceita:string, pessoa.tipo:string, textoPublicacao:string, linkPublicacao:string, detalhamentoPublicacao:string, numeroProcesso:string, abrangenciaDefinidaDecisaoJudicial:string, informacoesAdicionaisDoOrgaoSancionador:string

### GET /api-de-dados/ceaf
Consulta os registros do CEAF por CPF/Órgão de Lotação/Período — Filtros mínimos:  Página (padrão = 1);
- `cpfSancionado`: CPF do sancionado
- `nomeSancionado`: Nome do sancionado
- `orgaoLotacao`: Órgão de lotação
- `dataPublicacaoInicio`: Data publicação início (DD/MM/AAAA)
- `dataPublicacaoFim`: Data publicação fim (DD/MM/AAAA)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de CeafDTO): id:integer, dataPublicacao:string, dataReferencia:string, punicao:obj, punicao.cpfPunidoFormatado:string, punicao.nomePunido:string, punicao.portaria:string, punicao.processo:string, punicao.paginaDOU:string, punicao.secaoDOU:string, tipoPunicao:obj, tipoPunicao.descricao:string, pessoa:obj, pessoa.id:integer, pessoa.cpfFormatado:string, pessoa.cnpjFormatado:string, pessoa.numeroInscricaoSocial:string, pessoa.nome:string, pessoa.razaoSocialReceita:string, pessoa.nomeFantasiaReceita:string, pessoa.tipo:string, orgaoLotacao:obj, orgaoLotacao.siglaDaPasta:string, orgaoLotacao.sigla:string, orgaoLotacao.nome:string, orgaoLotacao.nomeSemAcento:string, ufLotacaoPessoa:obj, ufLotacaoPessoa.codigoIBGE:string, ufLotacaoPessoa.codigoCNPJEstado:string, ufLotacaoPessoa.populacao:integer, ufLotacaoPessoa.uf:obj, ufLotacaoPessoa.uf.sigla:string, ufLotacaoPessoa.uf.nome:string, cargoEfetivo:string, codigoCargoComissao:string, cargoComissao:string, fundamentacao:array, fundamentacao.codigo:string, fundamentacao.descricao:string

### GET /api-de-dados/ceaf/{id}
Consulta um registro do CEAF pelo id — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (objeto de CeafDTO): id:integer, dataPublicacao:string, dataReferencia:string, punicao:obj, punicao.cpfPunidoFormatado:string, punicao.nomePunido:string, punicao.portaria:string, punicao.processo:string, punicao.paginaDOU:string, punicao.secaoDOU:string, tipoPunicao:obj, tipoPunicao.descricao:string, pessoa:obj, pessoa.id:integer, pessoa.cpfFormatado:string, pessoa.cnpjFormatado:string, pessoa.numeroInscricaoSocial:string, pessoa.nome:string, pessoa.razaoSocialReceita:string, pessoa.nomeFantasiaReceita:string, pessoa.tipo:string, orgaoLotacao:obj, orgaoLotacao.siglaDaPasta:string, orgaoLotacao.sigla:string, orgaoLotacao.nome:string, orgaoLotacao.nomeSemAcento:string, ufLotacaoPessoa:obj, ufLotacaoPessoa.codigoIBGE:string, ufLotacaoPessoa.codigoCNPJEstado:string, ufLotacaoPessoa.populacao:integer, ufLotacaoPessoa.uf:obj, ufLotacaoPessoa.uf.sigla:string, ufLotacaoPessoa.uf.nome:string, cargoEfetivo:string, codigoCargoComissao:string, cargoComissao:string, fundamentacao:array, fundamentacao.codigo:string, fundamentacao.descricao:string

### GET /api-de-dados/acordos-leniencia
Consulta os registros de Acordos de Leniência por Nome ou CNPJ do Sancionado/Situação/Período — Filtros mínimos:  Página (padrão = 1);
- `cnpjSancionado`: CNPJ sancionado
- `nomeSancionado`: Nome, nome fantasia ou razão social do sancionado
- `situacao`: Situação do acordo
- `dataInicialSancao`: Data inicial da sanção (DD/MM/AAAA)
- `dataFinalSancao`: Data final da sanção (DD/MM/AAAA)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de AcordosLenienciaDTO): id:integer, dataInicioAcordo:string, dataFimAcordo:string, orgaoResponsavel:string, situacaoAcordo:string, sancoes:array, sancoes.nomeInformadoOrgaoResponsavel:string, sancoes.razaoSocial:string, sancoes.nomeFantasia:string, sancoes.cnpj:string, sancoes.cnpjFormatado:string, quantidade:integer

### GET /api-de-dados/acordos-leniencia/{id}
Consulta um registro de Acordo de Leniência pelo id — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (objeto de AcordosLenienciaDTO): id:integer, dataInicioAcordo:string, dataFimAcordo:string, orgaoResponsavel:string, situacaoAcordo:string, sancoes:array, sancoes.nomeInformadoOrgaoResponsavel:string, sancoes.razaoSocial:string, sancoes.nomeFantasia:string, sancoes.cnpj:string, sancoes.cnpjFormatado:string, quantidade:integer

## Servidores do Poder Executivo Federal

### GET /api-de-dados/servidores
Consulta todos servidores do Poder Executivo Federal — Filtros mínimos:  Página (padrão = 1); Código Órgão Lotação (SIAPE) OU Código Órgão Exercício (SIAPE) OU CPF;
- `tipoServidor`: Tipo do Servidor (Civil=1 ou Militar=2)
- `situacaoServidor`: Situação do Servidor (Ativo=1, Inativo=2 ou Pensionista=3)
- `cpf`: CPF do Servidor
- `nome`: Nome do Servidor
- `codigoFuncaoCargo`: Código da Função ou Cargo de Confiança
- `orgaoServidorExercicio`: Código Órgão Exercício (SIAPE)
- `orgaoServidorLotacao`: Código Órgão Lotação (SIAPE)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de CadastroServidorDTO): servidor:obj, servidor.id:integer, servidor.idServidorAposentadoPensionista:integer, servidor.pessoa:obj, servidor.pessoa.id:integer, servidor.pessoa.cpfFormatado:string, servidor.pessoa.cnpjFormatado:string, servidor.pessoa.numeroInscricaoSocial:string, servidor.pessoa.nome:string, servidor.pessoa.razaoSocialReceita:string, servidor.pessoa.nomeFantasiaReceita:string, servidor.pessoa.tipo:string, servidor.situacao:string, servidor.orgaoServidorLotacao:obj, servidor.orgaoServidorLotacao.codigo:string, servidor.orgaoServidorLotacao.nome:string, servidor.orgaoServidorLotacao.sigla:string, servidor.orgaoServidorLotacao.codigoOrgaoVinculado:string, servidor.orgaoServidorLotacao.nomeOrgaoVinculado:string, servidor.orgaoServidorExercicio:obj, servidor.orgaoServidorExercicio.codigo:string, servidor.orgaoServidorExercicio.nome:string, servidor.orgaoServidorExercicio.sigla:string, servidor.orgaoServidorExercicio.codigoOrgaoVinculado:string, servidor.orgaoServidorExercicio.nomeOrgaoVinculado:string, servidor.estadoExercicio:obj, servidor.estadoExercicio.sigla:string, servidor.estadoExercicio.nome:string, servidor.tipoServidor:string, servidor.funcao:obj, servidor.funcao.codigoFuncaoCargo:string, servidor.funcao.descricaoFuncaoCargo:string, servidor.servidorInativoInstuidorPensao:obj, servidor.servidorInativoInstuidorPensao.id:integer, servidor.servidorInativoInstuidorPensao.cpfFormatado:string, servidor.servidorInativoInstuidorPensao.nome:string, servidor.pensionistaRepresentante:obj, servidor.pensionistaRepresentante.id:integer, servidor.pensionistaRepresentante.cpfFormatado:string, servidor.pensionistaRepresentante.nome:string, servidor.codigoMatriculaFormatado:string, servidor.flagAfastado:integer, fichasCargoEfetivo:array, fichasCargoEfetivo.nome:string, fichasCargoEfetivo.cpfDescaracterizado:string, fichasCargoEfetivo.matriculaDescaracterizada:string, fichasCargoEfetivo.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasCargoEfetivo.diplomaLegal:string, fichasCargoEfetivo.jornadaTrabalho:string, fichasCargoEfetivo.regimeJuridico:string, fichasCargoEfetivo.situacaoServidor:string, fichasCargoEfetivo.afastamentos:array, fichasCargoEfetivo.orgaoSuperiorLotacao:string, fichasCargoEfetivo.orgaoLotacao:string, fichasCargoEfetivo.uorgLotacao:string, fichasCargoEfetivo.orgaoServidorLotacao:string, fichasCargoEfetivo.dataIngressoOrgao:string, fichasCargoEfetivo.dataIngressoServicoPublico:string, fichasCargoEfetivo.orgaoSuperiorExercicio:string, fichasCargoEfetivo.orgaoExercicio:string, fichasCargoEfetivo.orgaoServidorExercicio:string, fichasCargoEfetivo.uorgExercicio:string, fichasCargoEfetivo.cargo:string, fichasCargoEfetivo.classeCargo:string, fichasCargoEfetivo.padraoCargo:string, fichasCargoEfetivo.nivelCargo:string, fichasCargoEfetivo.dataIngressoCargo:string, fichasCargoEfetivo.formaIngresso:string, fichasCargoEfetivo.ufExercicio:string, fichasFuncao:array, fichasFuncao.nome:string, fichasFuncao.cpfDescaracterizado:string, fichasFuncao.matriculaDescaracterizada:string, fichasFuncao.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasFuncao.diplomaLegal:string, fichasFuncao.jornadaTrabalho:string, fichasFuncao.regimeJuridico:string, fichasFuncao.situacaoServidor:string, fichasFuncao.afastamentos:array, fichasFuncao.orgaoSuperiorLotacao:string, fichasFuncao.orgaoLotacao:string, fichasFuncao.uorgLotacao:string, fichasFuncao.orgaoServidorLotacao:string, fichasFuncao.dataIngressoOrgao:string, fichasFuncao.dataIngressoServicoPublico:string, fichasFuncao.orgaoSuperiorExercicio:string, fichasFuncao.orgaoExercicio:string, fichasFuncao.uorgExercicio:string, fichasFuncao.orgaoServidorExercicio:string, fichasFuncao.funcao:string, fichasFuncao.atividade:string, fichasFuncao.opcaoFuncao:string, fichasFuncao.dataIngressoFuncao:string, fichasFuncao.ufExercicio:string, fichasMilitar:array, fichasMilitar.nome:string, fichasMilitar.cpfDescaracterizado:string, fichasMilitar.matriculaDescaracterizada:string, fichasMilitar.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasMilitar.diplomaLegal:string, fichasMilitar.jornadaTrabalho:string, fichasMilitar.regimeJuridico:string, fichasMilitar.situacaoServidor:string, fichasMilitar.afastamentos:array, fichasMilitar.orgaoSuperior:string, fichasMilitar.orgao:string, fichasMilitar.orgaoServidorLotacao:string, fichasMilitar.cargo:string, fichasMilitar.dataIngressoOrgao:string, fichasDemaisSituacoes:array, fichasDemaisSituacoes.nome:string, fichasDemaisSituacoes.cpfDescaracterizado:string, fichasDemaisSituacoes.matriculaDescaracterizada:string, fichasDemaisSituacoes.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasDemaisSituacoes.diplomaLegal:string, fichasDemaisSituacoes.jornadaTrabalho:string, fichasDemaisSituacoes.regimeJuridico:string, fichasDemaisSituacoes.situacaoServidor:string, fichasDemaisSituacoes.afastamentos:array, fichasDemaisSituacoes.orgaoSuperiorLotacao:string, fichasDemaisSituacoes.orgaoLotacao:string, fichasDemaisSituacoes.uorgLotacao:string, fichasDemaisSituacoes.orgaoServidorLotacao:string, fichasDemaisSituacoes.dataIngressoOrgao:string, fichasDemaisSituacoes.dataIngressoServicoPublico:string, fichasAposentadoria:array, fichasAposentadoria.nome:string, fichasAposentadoria.cpfDescaracterizado:string, fichasAposentadoria.matriculaDescaracterizada:string, fichasAposentadoria.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasAposentadoria.diplomaLegal:string, fichasAposentadoria.jornadaTrabalho:string, fichasAposentadoria.regimeJuridico:string, fichasAposentadoria.situacaoServidor:string, fichasAposentadoria.afastamentos:array, fichasAposentadoria.orgaoSuperiorLotacao:string, fichasAposentadoria.orgaoLotacao:string, fichasAposentadoria.uorgLotacao:string, fichasAposentadoria.orgaoServidorLotacao:string, fichasAposentadoria.dataIngressoOrgao:string, fichasAposentadoria.dataIngressoServicoPublico:string, fichasAposentadoria.formaIngresso:string, fichasAposentadoria.dataIngressoCargo:string, fichasAposentadoria.cargo:string, fichasAposentadoria.tipoAposentadoria:string, fichasAposentadoria.fundamentacaoAposentadoria:string, fichasAposentadoria.dataAposentadoria:string, fichasReformado:array, fichasReformado.nome:string, fichasReformado.cpfDescaracterizado:string, fichasReformado.matriculaDescaracterizada:string, fichasReformado.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasReformado.diplomaLegal:string, fichasReformado.jornadaTrabalho:string, fichasReformado.regimeJuridico:string, fichasReformado.situacaoServidor:string, fichasReformado.afastamentos:array, fichasReformado.orgaoSuperior:string, fichasReformado.orgao:string, fichasReformado.orgaoServidorLotacao:string, fichasReformado.cargo:string, fichasReformado.dataIngressoOrgao:string, fichasReformado.tipoAposentadoria:string, fichasReformado.fundamentacaoAposentadoria:string, fichasReformado.dataReforma:string, fichasPensaoCivil:array, fichasPensaoCivil.nome:string, fichasPensaoCivil.cpfDescaracterizado:string, fichasPensaoCivil.matriculaDescaracterizada:string, fichasPensaoCivil.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasPensaoCivil.diplomaLegal:string, fichasPensaoCivil.jornadaTrabalho:string, fichasPensaoCivil.regimeJuridico:string, fichasPensaoCivil.situacaoServidor:string, fichasPensaoCivil.afastamentos:array, fichasPensaoCivil.orgaoSuperiorLotacao:string, fichasPensaoCivil.orgaoLotacao:string, fichasPensaoCivil.uorgLotacao:string, fichasPensaoCivil.orgaoServidorLotacao:string, fichasPensaoCivil.dataIngressoOrgao:string, fichasPensaoCivil.dataIngressoServicoPublico:string, fichasPensaoCivil.formaIngresso:string, fichasPensaoCivil.dataIngressoCargo:string, fichasPensaoCivil.cargo:string, fichasPensaoCivil.tipoPensao:string, fichasPensaoCivil.fundamentacaoPensao:string, fichasPensaoCivil.dataInicioPensao:string, fichasPensaoCivil.proporcaoPensao:string, fichasPensaoCivil.representanteLegal:string, fichasPensaoCivil.cpfRepresentanteLegal:string, fichasPensaoCivil.nomeInstituidor:string, fichasPensaoCivil.cpfInstituidor:string, fichasPensaoMilitar:array, fichasPensaoMilitar.nome:string, fichasPensaoMilitar.cpfDescaracterizado:string, fichasPensaoMilitar.matriculaDescaracterizada:string, fichasPensaoMilitar.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasPensaoMilitar.diplomaLegal:string, fichasPensaoMilitar.jornadaTrabalho:string, fichasPensaoMilitar.regimeJuridico:string, fichasPensaoMilitar.situacaoServidor:string, fichasPensaoMilitar.afastamentos:array, fichasPensaoMilitar.orgaoSuperior:string, fichasPensaoMilitar.orgao:string, fichasPensaoMilitar.orgaoServidorLotacao:string, fichasPensaoMilitar.cargo:string, fichasPensaoMilitar.dataIngressoOrgao:string, fichasPensaoMilitar.tipoPensao:string, fichasPensaoMilitar.fundamentacaoPensao:string, fichasPensaoMilitar.dataInicioPensao:string, fichasPensaoMilitar.proporcaoPensao:string, fichasPensaoMilitar.representanteLegal:string, fichasPensaoMilitar.cpfRepresentanteLegal:string, fichasPensaoMilitar.nomeInstituidor:string, fichasPensaoMilitar.cpfInstituidor:string

### GET /api-de-dados/servidores/{id}
Consulta um servidor do Poder Executivo Federal pelo idServidorAposentadoPensionista — Filtros mínimos: ID do registro
- `id` (obrigatório): idServidorAposentadoPensionista
- Resposta (objeto de CadastroServidorDTO): servidor:obj, servidor.id:integer, servidor.idServidorAposentadoPensionista:integer, servidor.pessoa:obj, servidor.pessoa.id:integer, servidor.pessoa.cpfFormatado:string, servidor.pessoa.cnpjFormatado:string, servidor.pessoa.numeroInscricaoSocial:string, servidor.pessoa.nome:string, servidor.pessoa.razaoSocialReceita:string, servidor.pessoa.nomeFantasiaReceita:string, servidor.pessoa.tipo:string, servidor.situacao:string, servidor.orgaoServidorLotacao:obj, servidor.orgaoServidorLotacao.codigo:string, servidor.orgaoServidorLotacao.nome:string, servidor.orgaoServidorLotacao.sigla:string, servidor.orgaoServidorLotacao.codigoOrgaoVinculado:string, servidor.orgaoServidorLotacao.nomeOrgaoVinculado:string, servidor.orgaoServidorExercicio:obj, servidor.orgaoServidorExercicio.codigo:string, servidor.orgaoServidorExercicio.nome:string, servidor.orgaoServidorExercicio.sigla:string, servidor.orgaoServidorExercicio.codigoOrgaoVinculado:string, servidor.orgaoServidorExercicio.nomeOrgaoVinculado:string, servidor.estadoExercicio:obj, servidor.estadoExercicio.sigla:string, servidor.estadoExercicio.nome:string, servidor.tipoServidor:string, servidor.funcao:obj, servidor.funcao.codigoFuncaoCargo:string, servidor.funcao.descricaoFuncaoCargo:string, servidor.servidorInativoInstuidorPensao:obj, servidor.servidorInativoInstuidorPensao.id:integer, servidor.servidorInativoInstuidorPensao.cpfFormatado:string, servidor.servidorInativoInstuidorPensao.nome:string, servidor.pensionistaRepresentante:obj, servidor.pensionistaRepresentante.id:integer, servidor.pensionistaRepresentante.cpfFormatado:string, servidor.pensionistaRepresentante.nome:string, servidor.codigoMatriculaFormatado:string, servidor.flagAfastado:integer, fichasCargoEfetivo:array, fichasCargoEfetivo.nome:string, fichasCargoEfetivo.cpfDescaracterizado:string, fichasCargoEfetivo.matriculaDescaracterizada:string, fichasCargoEfetivo.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasCargoEfetivo.diplomaLegal:string, fichasCargoEfetivo.jornadaTrabalho:string, fichasCargoEfetivo.regimeJuridico:string, fichasCargoEfetivo.situacaoServidor:string, fichasCargoEfetivo.afastamentos:array, fichasCargoEfetivo.orgaoSuperiorLotacao:string, fichasCargoEfetivo.orgaoLotacao:string, fichasCargoEfetivo.uorgLotacao:string, fichasCargoEfetivo.orgaoServidorLotacao:string, fichasCargoEfetivo.dataIngressoOrgao:string, fichasCargoEfetivo.dataIngressoServicoPublico:string, fichasCargoEfetivo.orgaoSuperiorExercicio:string, fichasCargoEfetivo.orgaoExercicio:string, fichasCargoEfetivo.orgaoServidorExercicio:string, fichasCargoEfetivo.uorgExercicio:string, fichasCargoEfetivo.cargo:string, fichasCargoEfetivo.classeCargo:string, fichasCargoEfetivo.padraoCargo:string, fichasCargoEfetivo.nivelCargo:string, fichasCargoEfetivo.dataIngressoCargo:string, fichasCargoEfetivo.formaIngresso:string, fichasCargoEfetivo.ufExercicio:string, fichasFuncao:array, fichasFuncao.nome:string, fichasFuncao.cpfDescaracterizado:string, fichasFuncao.matriculaDescaracterizada:string, fichasFuncao.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasFuncao.diplomaLegal:string, fichasFuncao.jornadaTrabalho:string, fichasFuncao.regimeJuridico:string, fichasFuncao.situacaoServidor:string, fichasFuncao.afastamentos:array, fichasFuncao.orgaoSuperiorLotacao:string, fichasFuncao.orgaoLotacao:string, fichasFuncao.uorgLotacao:string, fichasFuncao.orgaoServidorLotacao:string, fichasFuncao.dataIngressoOrgao:string, fichasFuncao.dataIngressoServicoPublico:string, fichasFuncao.orgaoSuperiorExercicio:string, fichasFuncao.orgaoExercicio:string, fichasFuncao.uorgExercicio:string, fichasFuncao.orgaoServidorExercicio:string, fichasFuncao.funcao:string, fichasFuncao.atividade:string, fichasFuncao.opcaoFuncao:string, fichasFuncao.dataIngressoFuncao:string, fichasFuncao.ufExercicio:string, fichasMilitar:array, fichasMilitar.nome:string, fichasMilitar.cpfDescaracterizado:string, fichasMilitar.matriculaDescaracterizada:string, fichasMilitar.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasMilitar.diplomaLegal:string, fichasMilitar.jornadaTrabalho:string, fichasMilitar.regimeJuridico:string, fichasMilitar.situacaoServidor:string, fichasMilitar.afastamentos:array, fichasMilitar.orgaoSuperior:string, fichasMilitar.orgao:string, fichasMilitar.orgaoServidorLotacao:string, fichasMilitar.cargo:string, fichasMilitar.dataIngressoOrgao:string, fichasDemaisSituacoes:array, fichasDemaisSituacoes.nome:string, fichasDemaisSituacoes.cpfDescaracterizado:string, fichasDemaisSituacoes.matriculaDescaracterizada:string, fichasDemaisSituacoes.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasDemaisSituacoes.diplomaLegal:string, fichasDemaisSituacoes.jornadaTrabalho:string, fichasDemaisSituacoes.regimeJuridico:string, fichasDemaisSituacoes.situacaoServidor:string, fichasDemaisSituacoes.afastamentos:array, fichasDemaisSituacoes.orgaoSuperiorLotacao:string, fichasDemaisSituacoes.orgaoLotacao:string, fichasDemaisSituacoes.uorgLotacao:string, fichasDemaisSituacoes.orgaoServidorLotacao:string, fichasDemaisSituacoes.dataIngressoOrgao:string, fichasDemaisSituacoes.dataIngressoServicoPublico:string, fichasAposentadoria:array, fichasAposentadoria.nome:string, fichasAposentadoria.cpfDescaracterizado:string, fichasAposentadoria.matriculaDescaracterizada:string, fichasAposentadoria.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasAposentadoria.diplomaLegal:string, fichasAposentadoria.jornadaTrabalho:string, fichasAposentadoria.regimeJuridico:string, fichasAposentadoria.situacaoServidor:string, fichasAposentadoria.afastamentos:array, fichasAposentadoria.orgaoSuperiorLotacao:string, fichasAposentadoria.orgaoLotacao:string, fichasAposentadoria.uorgLotacao:string, fichasAposentadoria.orgaoServidorLotacao:string, fichasAposentadoria.dataIngressoOrgao:string, fichasAposentadoria.dataIngressoServicoPublico:string, fichasAposentadoria.formaIngresso:string, fichasAposentadoria.dataIngressoCargo:string, fichasAposentadoria.cargo:string, fichasAposentadoria.tipoAposentadoria:string, fichasAposentadoria.fundamentacaoAposentadoria:string, fichasAposentadoria.dataAposentadoria:string, fichasReformado:array, fichasReformado.nome:string, fichasReformado.cpfDescaracterizado:string, fichasReformado.matriculaDescaracterizada:string, fichasReformado.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasReformado.diplomaLegal:string, fichasReformado.jornadaTrabalho:string, fichasReformado.regimeJuridico:string, fichasReformado.situacaoServidor:string, fichasReformado.afastamentos:array, fichasReformado.orgaoSuperior:string, fichasReformado.orgao:string, fichasReformado.orgaoServidorLotacao:string, fichasReformado.cargo:string, fichasReformado.dataIngressoOrgao:string, fichasReformado.tipoAposentadoria:string, fichasReformado.fundamentacaoAposentadoria:string, fichasReformado.dataReforma:string, fichasPensaoCivil:array, fichasPensaoCivil.nome:string, fichasPensaoCivil.cpfDescaracterizado:string, fichasPensaoCivil.matriculaDescaracterizada:string, fichasPensaoCivil.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasPensaoCivil.diplomaLegal:string, fichasPensaoCivil.jornadaTrabalho:string, fichasPensaoCivil.regimeJuridico:string, fichasPensaoCivil.situacaoServidor:string, fichasPensaoCivil.afastamentos:array, fichasPensaoCivil.orgaoSuperiorLotacao:string, fichasPensaoCivil.orgaoLotacao:string, fichasPensaoCivil.uorgLotacao:string, fichasPensaoCivil.orgaoServidorLotacao:string, fichasPensaoCivil.dataIngressoOrgao:string, fichasPensaoCivil.dataIngressoServicoPublico:string, fichasPensaoCivil.formaIngresso:string, fichasPensaoCivil.dataIngressoCargo:string, fichasPensaoCivil.cargo:string, fichasPensaoCivil.tipoPensao:string, fichasPensaoCivil.fundamentacaoPensao:string, fichasPensaoCivil.dataInicioPensao:string, fichasPensaoCivil.proporcaoPensao:string, fichasPensaoCivil.representanteLegal:string, fichasPensaoCivil.cpfRepresentanteLegal:string, fichasPensaoCivil.nomeInstituidor:string, fichasPensaoCivil.cpfInstituidor:string, fichasPensaoMilitar:array, fichasPensaoMilitar.nome:string, fichasPensaoMilitar.cpfDescaracterizado:string, fichasPensaoMilitar.matriculaDescaracterizada:string, fichasPensaoMilitar.dataPublicacaoDocumentoIngressoServicoPublico:string, fichasPensaoMilitar.diplomaLegal:string, fichasPensaoMilitar.jornadaTrabalho:string, fichasPensaoMilitar.regimeJuridico:string, fichasPensaoMilitar.situacaoServidor:string, fichasPensaoMilitar.afastamentos:array, fichasPensaoMilitar.orgaoSuperior:string, fichasPensaoMilitar.orgao:string, fichasPensaoMilitar.orgaoServidorLotacao:string, fichasPensaoMilitar.cargo:string, fichasPensaoMilitar.dataIngressoOrgao:string, fichasPensaoMilitar.tipoPensao:string, fichasPensaoMilitar.fundamentacaoPensao:string, fichasPensaoMilitar.dataInicioPensao:string, fichasPensaoMilitar.proporcaoPensao:string, fichasPensaoMilitar.representanteLegal:string, fichasPensaoMilitar.cpfRepresentanteLegal:string, fichasPensaoMilitar.nomeInstituidor:string, fichasPensaoMilitar.cpfInstituidor:string

### GET /api-de-dados/servidores/remuneracao
Consulta remunerações de um servidor do Poder Executivo Federal pelo CPF ou idServidorAposentadoPensionista e mês/ano — Filtros mínimos:  Página (padrão = 1);  CPF;  Ano/Mês (YYYYMM); ou Página (padrão = 1);  Id Servidor; Ano/Mês (YYYYMM);
- `id`: idServidorAposentadoPensionista
- `cpf`: CPF do Servidor
- `mesAno` (obrigatório): Ano e mês de referência (AAAAMM)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ServidorRemuneracaoDTO): servidor:obj, servidor.id:integer, servidor.idServidorAposentadoPensionista:integer, servidor.pessoa:obj, servidor.pessoa.id:integer, servidor.pessoa.cpfFormatado:string, servidor.pessoa.cnpjFormatado:string, servidor.pessoa.numeroInscricaoSocial:string, servidor.pessoa.nome:string, servidor.pessoa.razaoSocialReceita:string, servidor.pessoa.nomeFantasiaReceita:string, servidor.pessoa.tipo:string, servidor.situacao:string, servidor.orgaoServidorLotacao:obj, servidor.orgaoServidorLotacao.codigo:string, servidor.orgaoServidorLotacao.nome:string, servidor.orgaoServidorLotacao.sigla:string, servidor.orgaoServidorLotacao.codigoOrgaoVinculado:string, servidor.orgaoServidorLotacao.nomeOrgaoVinculado:string, servidor.orgaoServidorExercicio:obj, servidor.orgaoServidorExercicio.codigo:string, servidor.orgaoServidorExercicio.nome:string, servidor.orgaoServidorExercicio.sigla:string, servidor.orgaoServidorExercicio.codigoOrgaoVinculado:string, servidor.orgaoServidorExercicio.nomeOrgaoVinculado:string, servidor.estadoExercicio:obj, servidor.estadoExercicio.sigla:string, servidor.estadoExercicio.nome:string, servidor.tipoServidor:string, servidor.funcao:obj, servidor.funcao.codigoFuncaoCargo:string, servidor.funcao.descricaoFuncaoCargo:string, servidor.servidorInativoInstuidorPensao:obj, servidor.servidorInativoInstuidorPensao.id:integer, servidor.servidorInativoInstuidorPensao.cpfFormatado:string, servidor.servidorInativoInstuidorPensao.nome:string, servidor.pensionistaRepresentante:obj, servidor.pensionistaRepresentante.id:integer, servidor.pensionistaRepresentante.cpfFormatado:string, servidor.pensionistaRepresentante.nome:string, servidor.codigoMatriculaFormatado:string, servidor.flagAfastado:integer, remuneracoesDTO:array, remuneracoesDTO.skMesReferencia:string, remuneracoesDTO.mesAno:string, remuneracoesDTO.valorTotalRemuneracaoAposDeducoes:string, remuneracoesDTO.valorTotalRemuneracaoDolarAposDeducoes:string, remuneracoesDTO.valorTotalJetons:string, remuneracoesDTO.valorTotalHonorariosAdvocaticios:string, remuneracoesDTO.rubricas:array, remuneracoesDTO.rubricas.codigo:string, remuneracoesDTO.rubricas.descricao:string, remuneracoesDTO.rubricas.valor:number, remuneracoesDTO.rubricas.skMesReferencia:string, remuneracoesDTO.rubricas.valorDolar:number, remuneracoesDTO.jetons:array, remuneracoesDTO.jetons.descricao:string, remuneracoesDTO.jetons.valor:number, remuneracoesDTO.jetons.mesReferencia:string, remuneracoesDTO.honorariosAdvocaticios:array, remuneracoesDTO.honorariosAdvocaticios.mesReferencia:string, remuneracoesDTO.honorariosAdvocaticios.valor:number, remuneracoesDTO.honorariosAdvocaticios.mensagemMesReferencia:string, remuneracoesDTO.honorariosAdvocaticios.valorFormatado:string, remuneracoesDTO.observacoes:array, remuneracoesDTO.remuneracaoBasicaBruta:string, remuneracoesDTO.remuneracaoBasicaBrutaDolar:string, remuneracoesDTO.abateRemuneracaoBasicaBruta:string, remuneracoesDTO.abateRemuneracaoBasicaBrutaDolar:string, remuneracoesDTO.gratificacaoNatalina:string, remuneracoesDTO.gratificacaoNatalinaDolar:string, remuneracoesDTO.abateGratificacaoNatalina:string, remuneracoesDTO.abateGratificacaoNatalinaDolar:string, remuneracoesDTO.ferias:string, remuneracoesDTO.feriasDolar:string, remuneracoesDTO.outrasRemuneracoesEventuais:string, remuneracoesDTO.outrasRemuneracoesEventuaisDolar:string, remuneracoesDTO.impostoRetidoNaFonte:string, remuneracoesDTO.impostoRetidoNaFonteDolar:string, remuneracoesDTO.previdenciaOficial:string, remuneracoesDTO.previdenciaOficialDolar:string, remuneracoesDTO.outrasDeducoesObrigatorias:string, remuneracoesDTO.outrasDeducoesObrigatoriasDolar:string, remuneracoesDTO.pensaoMilitar:string, remuneracoesDTO.pensaoMilitarDolar:string, remuneracoesDTO.fundoSaude:string, remuneracoesDTO.fundoSaudeDolar:string, remuneracoesDTO.taxaOcupacaoImovelFuncional:string, remuneracoesDTO.taxaOcupacaoImovelFuncionalDolar:string, remuneracoesDTO.verbasIndenizatoriasCivil:string, remuneracoesDTO.verbasIndenizatoriasCivilDolar:string, remuneracoesDTO.verbasIndenizatoriasMilitar:string, remuneracoesDTO.verbasIndenizatoriasMilitarDolar:string, remuneracoesDTO.verbasIndenizatoriasReferentesPDV:string, remuneracoesDTO.verbasIndenizatoriasReferentesPDVDolar:string, remuneracoesDTO.remuneracaoEmpresaPublica:boolean, remuneracoesDTO.existeValorMes:boolean, remuneracoesDTO.mesAnoPorExtenso:string, remuneracoesDTO.verbasIndenizatorias:string, remuneracoesDTO.verbasIndenizatoriasDolar:string

### GET /api-de-dados/servidores/por-orgao
Consulta de servidores agregados por órgão — Filtros mínimos:  Página (padrão = 1);
- `orgaoLotacao`: Código Órgão Lotação (SIAPE)
- `orgaoExercicio`: Código Órgão Exercício (SIAPE)
- `tipoServidor`: Tipo servidor (Civil: 1; Militar: 2)
- `tipoVinculo`: Tipo vínculo (Função: 1; Cargo: 2; Outros: 3; Militares: 4
- `licenca`: Licença (Sim: 1; Não: 0)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ServidorPorOrgaoDTO): qntPessoas:integer, qntVinculos:integer, skSituacao:integer, descSituacao:string, skTipoVinculo:integer, descTipoVinculo:string, skTipoServidor:integer, descTipoServidor:string, licenca:integer, codOrgaoExercicioSiape:string, nomOrgaoExercicioSiape:string, codOrgaoSuperiorExercicioSiape:string, nomOrgaoSuperiorExercicioSiape:string

### GET /api-de-dados/servidores/funcoes-e-cargos
Código da Função ou Cargo de Confiança — Filtros mínimos:  Página (padrão = 1);
- `pagina` (obrigatório): Página consultada
- Resposta (lista de FuncaoServidorDTO): codigoFuncaoCargo:string, descricaoFuncaoCargo:string

### GET /api-de-dados/peps
Consulta PEPs — 
- `cpf`: CPF do Servidor
- `nome`: Nome do Servidor
- `descricaoFuncao`: Descrição da Função
- `orgaoServidorLotacao`: Código Órgão Lotação (SIAPE)
- `dataInicioExercicioDe`: Data início do exercício, período inicial (DD/MM/AAAA)
- `datInicioExercicioAte`: Data início do exercício, período final (DD/MM/AAAA)
- `dataFimExercicioDe`: Data fim do exercício, período inicial (DD/MM/AAAA)
- `datFimExercicioAte`: Data fim do exercício, período final (DD/MM/AAAA)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de PEPDTO): cpf:string, nome:string, sigla_funcao:string, descricao_funcao:string, nivel_funcao:string, cod_orgao:string, nome_orgao:string, dt_inicio_exercicio:string, dt_fim_exercicio:string, dt_fim_carencia:string

## Viagens a serviço

### GET /api-de-dados/viagens
Consulta viagens por período — Filtros mínimos:  Página (padrão = 1);  Período de no máximo 1 mês; Código do Órgão (SIAFI)
- `dataIdaDe` (obrigatório): Data de ida a partir de (DD/MM/AAAA)
- `dataIdaAte` (obrigatório): Data de ida até (DD/MM/AAAA)
- `dataRetornoDe` (obrigatório): Data de retorno a partir de (DD/MM/AAAA)
- `dataRetornoAte` (obrigatório): Data de retorno até (DD/MM/AAAA)
- `codigoOrgao` (obrigatório): Código do Órgão (SIAFI)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ViagemDTO): id:integer, viagem:obj, viagem.motivo:string, viagem.pcdp:string, viagem.ano:integer, viagem.numPcdp:string, viagem.justificativaUrgente:string, viagem.urgenciaViagem:string, situacao:string, beneficiario:obj, beneficiario.cpfFormatado:string, beneficiario.nis:string, beneficiario.nome:string, cargo:obj, cargo.codigoSIAPE:string, cargo.descricao:string, funcao:obj, funcao.codigoSIAPE:string, funcao.descricao:string, tipoViagem:string, orgao:obj, orgao.nome:string, orgao.codigoSIAFI:string, orgao.cnpj:string, orgao.sigla:string, orgao.descricaoPoder:string, orgao.orgaoMaximo:obj, orgao.orgaoMaximo.codigo:string, orgao.orgaoMaximo.sigla:string, orgao.orgaoMaximo.nome:string, orgaoPagamento:obj, orgaoPagamento.nome:string, orgaoPagamento.codigoSIAFI:string, orgaoPagamento.cnpj:string, orgaoPagamento.sigla:string, orgaoPagamento.descricaoPoder:string, orgaoPagamento.orgaoMaximo:obj, orgaoPagamento.orgaoMaximo.codigo:string, orgaoPagamento.orgaoMaximo.sigla:string, orgaoPagamento.orgaoMaximo.nome:string, unidadeGestoraResponsavel:obj, unidadeGestoraResponsavel.codigo:string, unidadeGestoraResponsavel.nome:string, unidadeGestoraResponsavel.descricaoPoder:string, unidadeGestoraResponsavel.orgaoVinculado:obj, unidadeGestoraResponsavel.orgaoVinculado.codigoSIAFI:string, unidadeGestoraResponsavel.orgaoVinculado.cnpj:string, unidadeGestoraResponsavel.orgaoVinculado.sigla:string, unidadeGestoraResponsavel.orgaoVinculado.nome:string, unidadeGestoraResponsavel.orgaoMaximo:obj, unidadeGestoraResponsavel.orgaoMaximo.codigo:string, unidadeGestoraResponsavel.orgaoMaximo.sigla:string, unidadeGestoraResponsavel.orgaoMaximo.nome:string, dataInicioAfastamento:string, dataFimAfastamento:string, valorTotalRestituicao:number, valorTotalTaxaAgenciamento:number, valorMulta:number, valorTotalDiarias:number, valorTotalPassagem:number, valorTotalViagem:number, valorTotalDevolucao:number

### GET /api-de-dados/viagens/{id}
Consulta uma viagem pelo ID — Filtros mínimos: ID do registro
- `id` (obrigatório): ID do registro
- Resposta (objeto de ViagemDTO): id:integer, viagem:obj, viagem.motivo:string, viagem.pcdp:string, viagem.ano:integer, viagem.numPcdp:string, viagem.justificativaUrgente:string, viagem.urgenciaViagem:string, situacao:string, beneficiario:obj, beneficiario.cpfFormatado:string, beneficiario.nis:string, beneficiario.nome:string, cargo:obj, cargo.codigoSIAPE:string, cargo.descricao:string, funcao:obj, funcao.codigoSIAPE:string, funcao.descricao:string, tipoViagem:string, orgao:obj, orgao.nome:string, orgao.codigoSIAFI:string, orgao.cnpj:string, orgao.sigla:string, orgao.descricaoPoder:string, orgao.orgaoMaximo:obj, orgao.orgaoMaximo.codigo:string, orgao.orgaoMaximo.sigla:string, orgao.orgaoMaximo.nome:string, orgaoPagamento:obj, orgaoPagamento.nome:string, orgaoPagamento.codigoSIAFI:string, orgaoPagamento.cnpj:string, orgaoPagamento.sigla:string, orgaoPagamento.descricaoPoder:string, orgaoPagamento.orgaoMaximo:obj, orgaoPagamento.orgaoMaximo.codigo:string, orgaoPagamento.orgaoMaximo.sigla:string, orgaoPagamento.orgaoMaximo.nome:string, unidadeGestoraResponsavel:obj, unidadeGestoraResponsavel.codigo:string, unidadeGestoraResponsavel.nome:string, unidadeGestoraResponsavel.descricaoPoder:string, unidadeGestoraResponsavel.orgaoVinculado:obj, unidadeGestoraResponsavel.orgaoVinculado.codigoSIAFI:string, unidadeGestoraResponsavel.orgaoVinculado.cnpj:string, unidadeGestoraResponsavel.orgaoVinculado.sigla:string, unidadeGestoraResponsavel.orgaoVinculado.nome:string, unidadeGestoraResponsavel.orgaoMaximo:obj, unidadeGestoraResponsavel.orgaoMaximo.codigo:string, unidadeGestoraResponsavel.orgaoMaximo.sigla:string, unidadeGestoraResponsavel.orgaoMaximo.nome:string, dataInicioAfastamento:string, dataFimAfastamento:string, valorTotalRestituicao:number, valorTotalTaxaAgenciamento:number, valorMulta:number, valorTotalDiarias:number, valorTotalPassagem:number, valorTotalViagem:number, valorTotalDevolucao:number

### GET /api-de-dados/viagens-por-cpf
Consulta viagens por CPF — Filtros mínimos:  Página (padrão = 1);  CPF;
- `cpf` (obrigatório): CPF
- `pagina` (obrigatório): Página consultada
- Resposta (lista de ViagemDTO): id:integer, viagem:obj, viagem.motivo:string, viagem.pcdp:string, viagem.ano:integer, viagem.numPcdp:string, viagem.justificativaUrgente:string, viagem.urgenciaViagem:string, situacao:string, beneficiario:obj, beneficiario.cpfFormatado:string, beneficiario.nis:string, beneficiario.nome:string, cargo:obj, cargo.codigoSIAPE:string, cargo.descricao:string, funcao:obj, funcao.codigoSIAPE:string, funcao.descricao:string, tipoViagem:string, orgao:obj, orgao.nome:string, orgao.codigoSIAFI:string, orgao.cnpj:string, orgao.sigla:string, orgao.descricaoPoder:string, orgao.orgaoMaximo:obj, orgao.orgaoMaximo.codigo:string, orgao.orgaoMaximo.sigla:string, orgao.orgaoMaximo.nome:string, orgaoPagamento:obj, orgaoPagamento.nome:string, orgaoPagamento.codigoSIAFI:string, orgaoPagamento.cnpj:string, orgaoPagamento.sigla:string, orgaoPagamento.descricaoPoder:string, orgaoPagamento.orgaoMaximo:obj, orgaoPagamento.orgaoMaximo.codigo:string, orgaoPagamento.orgaoMaximo.sigla:string, orgaoPagamento.orgaoMaximo.nome:string, unidadeGestoraResponsavel:obj, unidadeGestoraResponsavel.codigo:string, unidadeGestoraResponsavel.nome:string, unidadeGestoraResponsavel.descricaoPoder:string, unidadeGestoraResponsavel.orgaoVinculado:obj, unidadeGestoraResponsavel.orgaoVinculado.codigoSIAFI:string, unidadeGestoraResponsavel.orgaoVinculado.cnpj:string, unidadeGestoraResponsavel.orgaoVinculado.sigla:string, unidadeGestoraResponsavel.orgaoVinculado.nome:string, unidadeGestoraResponsavel.orgaoMaximo:obj, unidadeGestoraResponsavel.orgaoMaximo.codigo:string, unidadeGestoraResponsavel.orgaoMaximo.sigla:string, unidadeGestoraResponsavel.orgaoMaximo.nome:string, dataInicioAfastamento:string, dataFimAfastamento:string, valorTotalRestituicao:number, valorTotalTaxaAgenciamento:number, valorMulta:number, valorTotalDiarias:number, valorTotalPassagem:number, valorTotalViagem:number, valorTotalDevolucao:number

## api-funcional-programatica-controller

### GET /api-de-dados/despesas/funcional-programatica/subfuncoes
 — 
- `anoInicio` (obrigatório): 
- `codigo`: 
- `pagina` (obrigatório): 
- Resposta (lista de DimFuncionalProgramaticaDTO): id:integer, codigo:string, descricao:string, ano:integer

### GET /api-de-dados/despesas/funcional-programatica/programas
 — 
- `anoInicio` (obrigatório): 
- `codigo`: 
- `pagina` (obrigatório): 
- Resposta (lista de DimFuncionalProgramaticaDTO): id:integer, codigo:string, descricao:string, ano:integer

### GET /api-de-dados/despesas/funcional-programatica/listar
 — 
- `ano` (obrigatório): 
- `pagina` (obrigatório): 
- Resposta (lista de FuncionalProgramaticaDTO): id:integer, codigoFuncao:string, codigoSubfuncao:string, codigoPrograma:string, codigoAcao:string, ano:integer

### GET /api-de-dados/despesas/funcional-programatica/funcoes
 — 
- `anoInicio` (obrigatório): 
- `codigo`: 
- `pagina` (obrigatório): 
- Resposta (lista de DimFuncionalProgramaticaDTO): id:integer, codigo:string, descricao:string, ano:integer

### GET /api-de-dados/despesas/funcional-programatica/acoes
 — 
- `anoInicio` (obrigatório): 
- `codigo`: 
- `pagina` (obrigatório): 
- Resposta (lista de DimFuncionalProgramaticaDTO): id:integer, codigo:string, descricao:string, ano:integer

## Órgãos

### GET /api-de-dados/orgaos-siape
Consulta de órgãos cadastrados no Sistema Integrado de Administração de Pessoal (SIAPE) — Filtros mínimos:  Página (padrão = 1);  Período de no máximo 1 mês;
- `codigo`: Código do Órgão (SIAPE)
- `descricao`: Descrição do Órgão (SIAPE)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de CodigoDescricaoDTO): codigo:string, descricao:string

### GET /api-de-dados/orgaos-siafi
Consulta de órgãos cadastrados no Sistema Integrado de Administração Financeira do Governo Federal (SIAFI) — Filtros mínimos:  Página (padrão = 1);
- `codigo`: Código do Órgão (SIAFI)
- `descricao`: Descrição do Órgão (SIAFI)
- `pagina` (obrigatório): Página consultada
- Resposta (lista de CodigoDescricaoDTO): codigo:string, descricao:string