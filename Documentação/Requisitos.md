# Requisitos do Projeto

### Requisitos Funcionais

1.  **RF01:** O sistema deve ser capaz de receber arquivos de cotações diárias e armazená-los no Azure Blob Storage.
2.  **RF02:** O sistema deve extrair as seguintes informações dos arquivos: código do ativo, data do pregão, preço de abertura, preço de fechamento e volume financeiro.
3.  **RF03:** O sistema deve transformar os dados extraídos para um formato estruturado e limpo.
4.  **RF04:** O sistema deve carregar os dados transformados em uma tabela chamada `Cotacoes` no Azure SQL Database.
5.  **RF05:** O carregamento no banco de dados deve ser incremental, evitando duplicidade de dados.
6.  **RF06:** O sistema deve enviar uma notificação por e-mail após a conclusão do processo de carga.
7.  **RF07:** O pipeline de dados deve ser automatizado, iniciando a partir da chegada de um novo arquivo.

### Requisitos Não-Funcionais

1.  **RNF01:** A solução deve ser construída utilizando os serviços da plataforma Microsoft Azure.
2.  **RNF02:** A arquitetura deve ser escalável para suportar um grande volume de dados (*Big Data*).
3.  **RNF03:** A solução deve utilizar computação *serverless* (Azure Functions) para a lógica de carga, otimizando custos.
4.  **RNF04:** A ingestão de dados deve ser simulada por um container Docker.
5.  **RNF05:** O código da Azure Function deve ser escrito em Python.
6.  **RNF06:** A segurança das chaves e conexões (connection strings) deve ser gerenciada de forma segura (ex: Azure Key Vault).
