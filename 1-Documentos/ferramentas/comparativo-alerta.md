# Comparativo de canais de alerta

Usado como base do ADR 0003 (`1-Documentos/adrs/0003-canal-de-alerta.md`). Critérios de `criterios.md`. Nada aqui foi testado no órgão: o que depende de permissão do órgão está marcado **a confirmar**.

## Canais comparados

1. **Webhook HTTPS** para Teams (Workflows/conector de entrada), Slack (Incoming Webhook) ou Google Chat. É o que `3-Etl/dags/scdp/alerta.py` implementa: POST JSON `{"text": ...}`.
2. **E-mail SMTP** (envio direto ou pelo `EmailOperator`/`send_email` do Airflow).
3. **Log e e-mail nativo do Airflow** (falha da tarefa na interface, `email_on_failure`).

## Matriz

| Critério | Webhook HTTPS (Teams, Slack, Google Chat) | E-mail SMTP | Log / e-mail nativo do Airflow |
|---|---|---|---|
| Custo | Sem custo adicional se o órgão já tem o chat; webhook em plano pago ou restrito é a confirmar | Sem custo se houver relay SMTP interno | Nenhum |
| Licenca | Uso do recurso do chat já licenciado; Teams e Slack podem limitar webhooks por plano ou política (a confirmar) | Servidor SMTP do órgão | Airflow é Apache 2.0; nada a licenciar |
| Segredo | A própria URL é o segredo (quem a tem posta no canal). Fica em `ALERTA_WEBHOOK_URL` no ambiente do worker ou numa Connection do Airflow; nunca no repositório | Usuário e senha SMTP; mesmo cuidado, e exige mais campos | Sem segredo novo; o SMTP do Airflow guarda o seu em `airflow.cfg`/Connection |
| Esforco | Baixo: um POST HTTPS, sem dependência extra; código pronto e testado | Médio: relay liberado, autenticação, remetente e lista de destinatários | Nenhum para o log; e-mail exige SMTP configurado no Airflow |
| Confiabilidade | Boa, mas depende do serviço externo e de a URL não ser revogada; falha de envio é silenciosa para a carga | Boa; e-mail é assíncrono e pode ir para spam; bloqueios de saída são comuns em redes de governo (a confirmar) | O log sempre existe, mas ninguém é avisado; e-mail nativo tem a confiabilidade do SMTP |
| Rede | Saída HTTPS para o domínio do chat precisa estar liberada (a confirmar) | Saída para a porta SMTP do relay | Nenhuma |

## Segredo e falha de cada canal

- **Webhook:** segredo é a URL. Se for exposta, revogar e gerar outra. Se o canal cair, `alertar` devolve `FALHA_ENVIO` e a carga segue; a falha continua visível no Airflow. Sem a variável, devolve `NAO_CONFIGURADO`.
- **SMTP:** segredo é a credencial do relay. Se o SMTP cair, o e-mail se perde ou fica na fila do servidor; a tarefa falha do mesmo jeito e o Airflow registra.
- **Airflow nativo:** não há segredo extra. Se ninguém olhar a interface, a falha passa despercebida, que é o motivo de existir um canal ativo.

## Conclusão para o ADR

O webhook HTTPS tem o menor esforço e já está implementado, com o log do Airflow como rede de segurança (a falha da tarefa continua registrada mesmo se o envio falhar). SMTP fica como alternativa se o órgão bloquear webhooks de chat. Confirmar com o órgão: qual chat é permitido (Teams, Slack ou Google Chat), se webhooks de entrada estão liberados e se há saída HTTPS do servidor do Airflow.
