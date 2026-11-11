# ADR 0003: canal de alerta de falha da carga

Status: Proposto (aguarda confirmação do órgão sobre o uso de webhook)

Data: 2026-11-11. Base: `1-Documentos/ferramentas/comparativo-alerta.md`.

## Contexto

As DAGs (`scdp_carga_diaria`, `scdp_carga_completa`) rodam sem acompanhamento e uma falha só aparece na interface do Airflow. O módulo `3-Etl/dags/scdp/alerta.py` já existe e é usado como `on_failure_callback` das tarefas. Falta decidir o canal e onde mora o segredo.

## Decisão proposta

Webhook HTTPS para o chat do órgão (Teams, Slack ou Google Chat, conforme o que o órgão permitir; **a confirmar**).

- `alerta.py` envia POST JSON `{"text": ...}` para a URL de `ALERTA_WEBHOOK_URL`. Só aceita `https://`.
- A URL é segredo. Fica no ambiente do worker do Airflow (ou numa Connection do Airflow, ainda não usada pelo projeto) e **nunca** no repositório, no `.env.example` com valor, em log ou em mensagem. A mensagem passa por `mascarar`, que troca a URL, a chave da API e a senha do banco por `***`.
- Sem a variável, o envio devolve `NAO_CONFIGURADO` e nada acontece. Falha de envio (rede, HTTP fora de 2xx, URL sem https) devolve `FALHA_ENVIO`. Em nenhum caso o alerta levanta exceção: ele não pode esconder a falha que avisa.
- A DAG diária não alerta quando a tarefa sai com o código de "trava ocupada" (`CODIGO_OCUPADO`), porque isso é esperado.

## Alternativas rejeitadas

- **E-mail SMTP:** mais configuração (relay, autenticação, remetente, destinatários), credencial com mais campos e bloqueios de saída comuns em redes de governo. Fica como plano B se o webhook não for permitido.
- **Teams ou Slack por aplicativo/bot nativo (OAuth):** exige registro de aplicativo, tokens com ciclo de renovação e aprovação do administrador do chat; muito esforço para uma mensagem de texto. O webhook cobre o caso.
- **Só o log do Airflow:** sem custo, mas ninguém é avisado; a falha só é vista se alguém abrir a interface. Continua existindo como registro, não como alerta.

## Consequencias

- Se o canal falhar (URL revogada, chat fora do ar, rede bloqueada), a carga não é afetada e a tarefa continua marcada como falha no Airflow, que segue como fonte da verdade. O alerta perdido não é reenviado.
- Rotina de proteção: conferir periodicamente a saúde pelas views `vw_ctl_saude` e `vw_ctl_erros_abertos`, que não dependem do chat. Se o envio passar a falhar de forma contínua, avaliar o plano B (SMTP).
- A URL do webhook precisa de rotação quando alguém sair da equipe ou se vazar: gerar nova no chat, atualizar o ambiente do worker e revogar a antiga.
- Sem Connections/Variables do Airflow ainda, o segredo depende do ambiente do worker; migrar junto com a chave da API e a senha do banco (ver `ambiente-airflow.md`).
- Pendente fora do código: confirmar com o órgão qual chat é permitido, se webhooks de entrada estão liberados e se o servidor do Airflow tem saída HTTPS para ele.
