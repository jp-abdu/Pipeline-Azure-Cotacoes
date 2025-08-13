# Casos de Uso

### Caso de Uso 1: Ingestão de Novos Arquivos de Cotação

* **Ator:** Sistema Automatizado (Simulado via Docker Container)
* **Descrição:** O sistema obtém o arquivo diário de cotações da B3 e o carrega na área de dados brutos (*raw*) do Azure Blob Storage.
* **Fluxo:**
    1.  Um container Docker é executado para simular a extração e envio dos arquivos.
    2.  Ele envia um novo arquivo de cotações para a pasta designada no Blob Storage.
    3.  A chegada do novo arquivo serve como gatilho para iniciar o pipeline de dados.

### Caso de Uso 2: Processamento e Carga de Dados

* **Ator:** Engenheiro de Dados (Desenvolvedor do Pipeline)
* **Descrição:** O pipeline do Azure Data Factory é acionado para processar o arquivo recém-chegado, transformá-lo e carregá-lo no banco de dados.
* **Fluxo:**
    1.  O Data Factory copia o arquivo da área bruta para a área de processamento.
    2.  Aplica as transformações necessárias (limpeza, seleção de colunas, conversão de tipos).
    3.  Chama a Azure Function para realizar a carga incremental dos dados tratados na tabela `Cotacoes` do Azure SQL Database.

### Caso de Uso 3: Notificação sobre o Status do Pipeline

* **Ator:** Administrador do Sistema
* **Descrição:** Ao final da execução do pipeline, o sistema envia uma notificação por e-mail informando o resultado (sucesso ou falha).
* **Fluxo:**
    1.  O Data Factory conclui sua execução.
    2.  A Logic App é acionada pelo status final do pipeline para automação de alertas.
    3.  A Logic App envia um e-mail formatado para a lista de destinatários cadastrados.
