# Projeto: Pipeline Cloud para Análise de Cotações da B3 com Azure

## Objetivo do Projeto

Este projeto educacional tem como finalidade construir uma arquitetura de dados completa na nuvem Microsoft Azure para processar arquivos de cotações diárias da B3 (Bolsa de Valores do Brasil). O foco é aplicar conceitos de Big Data e engenharia de dados em um cenário prático, desenvolvendo habilidades em arquitetura cloud, automação de pipelines e integração de serviços.

## Contexto

A B3 disponibiliza diariamente arquivos com informações detalhadas das cotações do pregão, incluindo dados como código do ativo, data, preços de abertura, máximo, mínimo, fechamento e volume financeiro. O desafio é criar uma solução automatizada que extraia esses dados, realize as transformações necessárias, armazene-os de forma estruturada em um banco de dados e os disponibilize para análise e visualização.

##  Arquitetura da Solução

A solução proposta utiliza um conjunto de serviços do Azure para orquestrar o fluxo de dados, desde a ingestão até a análise:

* **Azure Storage Account:** Repositório central para armazenar os arquivos brutos (originais da B3) e os arquivos já processados.
* **Azure Data Factory:** Ferramenta de ETL (Extração, Transformação e Carga) responsável por orquestrar o pipeline que copia os dados, aplica as transformações e os salva no destino.
* **Azure Function:** Componente de computação *serverless* utilizado para realizar a carga incremental dos dados transformados no banco de dados.
* **Azure SQL Database:** Banco de dados relacional na nuvem onde as cotações processadas e limpas são armazenadas para consulta e análise.
* **Logic Apps:** Serviço de automação que envia notificações por e-mail sobre o status do processo e pode se integrar com ferramentas de visualização como o Power BI.
* **Docker + Azure Container Instance:** Utilizado para simular a extração e o envio dos arquivos de cotações para o Azure Blob Storage, iniciando o pipeline.

## Fluxo do Processo

O projeto segue um fluxo de dados bem definido:

1.  **Ingestão:** Um container Docker simula a obtenção dos arquivos da B3 e os envia para o Azure Blob Storage.
2.  **Transformação:** O Azure Data Factory é acionado, processa os arquivos brutos, limpando e formatando os dados.
3.  **Carga:** Uma Azure Function é executada para carregar os dados transformados de forma incremental no Azure SQL Database.
4.  **Automação e Alertas:** A Logic App monitora o processo e envia alertas (ex: sucesso ou falha) por e-mail.
5.  **Visualização (Opcional):** Os dados armazenados no banco de dados podem ser consumidos por ferramentas como Power BI ou Synapse Analytics para criação de dashboards.

##  Artefatos

Os principais entregáveis deste projeto são:

* Documento de Arquitetura e Fluxo do processo.
* Pipeline funcional no Azure Data Factory.
* Código da Azure Function em Python.
* Container Docker para simulação da ingestão.
* Logic App configurada para notificações.
* Script para criação da tabela `Cotacoes` no Azure SQL.

## Links Úteis da B3

* **Cotações Históricas:** [https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/mercado-a-vista/cotacoes-historicas/](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/mercado-a-vista/cotacoes-historicas/)
* **Boletim Diário do Mercado:** [https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/boletins-diarios/pesquisa-por-pregao/pesquisa-por-pregao/](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/boletins-diarios/pesquisa-por-pregao/pesquisa-por-pregao/)
* **Layout dos Arquivos:** [https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/boletins-diarios/pesquisa-por-pregao/layout-dos-arquivos/](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/boletins-diarios/pesquisa-por-pregao/layout-dos-arquivos/)
