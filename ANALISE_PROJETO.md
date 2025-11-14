# 📊 Análise do Projeto - Pipeline Azure Cotações B3

## 🎯 Resumo Executivo

Este projeto implementa um **pipeline de dados na nuvem Azure** para processar cotações diárias da B3 (Bolsa de Valores). O objetivo é extrair, transformar e disponibilizar dados de ativos financeiros através de uma aplicação web completa.

---

## 🏗️ Arquitetura Atual (O que já está implementado)

### 1️⃣ **Backend - Spring Boot (Java)** ✅

**Localização:** `Projeto Cloud/backend/`

**Tecnologias:**

- Spring Boot 3.5.7
- Java 21
- Spring Data JPA
- MySQL Connector
- Lombok
- OpenAPI/Swagger 2.6.0

**Funcionalidades Implementadas:**

- ✅ API REST para consulta de ativos
- ✅ Endpoint: `GET /api/assets` com filtros (nome, data início, data fim, paginação)
- ✅ Endpoint: `GET /api/assets/{id}` para busca por ID
- ✅ Entidade `Asset` mapeada para tabela `asset` com campos:
  - `id` (Long, auto-increment)
  - `nome` (String - código do ativo)
  - `volumeDiario` (BigDecimal)
  - `precoFechamento` (BigDecimal)
  - `precoAbertura` (BigDecimal)
  - `dataPregao` (LocalDate)
  - `precoMedio` (BigDecimal)
- ✅ Repository com query customizada para busca com filtros
- ✅ CORS configurado para aceitar todas as origens
- ✅ **Conectado a MySQL no Azure:** `ativos-b3-ibmec.mysql.database.azure.com/ativosb3`

**Status:** ⚠️ **FUNCIONAL mas precisa ser publicado no Azure Web App**

---

### 2️⃣ **Frontend - React** ✅

**Localização:** `Projeto Cloud/frontend/`

**Tecnologias:**

- React 18.3.1
- Material-UI (MUI) 6.1.3
- Axios para requisições HTTP
- Recharts para gráficos
- Day.js para manipulação de datas

**Funcionalidades Implementadas:**

- ✅ Dashboard de ativos com visualização em tabela
- ✅ Gráficos de cotações (componente AssetChart)
- ✅ Filtros de busca por nome e data (componente Filters)
- ✅ Tabela paginada de ativos (componente AssetTable)
- ✅ **API configurada para:** `https://projeto-cloud-b3-fkhpfyhufbd4hbbk.brazilsouth-01.azurewebsites.net/api`
- ✅ Build já gerado na pasta `build/`

**Status:** ⚠️ **FUNCIONAL mas precisa ser publicado no Azure (Static Web App ou Storage Account)**

---

### 3️⃣ **Azure Function - Extração (Time Trigger)** ✅

**Localização:** `Projeto Cloud/function_extract/`

**Tecnologias:**

- Python 3.x
- Azure Functions
- Azure Storage Blob SDK
- Requests (para download)
- lxml

**Funcionalidades Implementadas:**

- ✅ **Timer Trigger:** Executa a cada 30 segundos (`schedule="*/30 * * * * *"`)
- ✅ Baixa arquivos de cotações da B3 (formato ZIP)
- ✅ Extrai arquivos XML dos ZIPs (dupla extração)
- ✅ Faz upload dos arquivos XML para Azure Blob Storage
- ✅ Gerenciamento de arquivos temporários em `/tmp/dados_b3`
- ✅ Logging completo do processo
- ⚠️ **Data hardcoded:** `dt = "251107"` (precisa ser dinâmica)

**Dependências:**

```python
azure-storage-blob
azure-functions
requests
lxml
```

**Variáveis de Ambiente Necessárias:**

- `AZURESTORAGE_CONNECTION_STRING` - Connection string do Storage Account
- `AZURESTORAGE_CONTAINER_NAME` - Nome do container (default: `dados-pregao-bolsa`)

**Status:** ⚠️ **IMPLEMENTADO mas precisa ser publicado no Azure + ajustes na data**

---

### 4️⃣ **Azure Function - Carga (Blob Trigger)** ⚠️

**Localização:** `Projeto Cloud/function_load/`

**Tecnologias:**

- Python 3.x
- Azure Functions

**Funcionalidades Implementadas:**

- ✅ **Blob Trigger:** Dispara quando novo arquivo chega no container `arquivosb3`
- ❌ **Lógica de processamento NÃO implementada** - apenas logging básico
- ❌ Não faz parse do XML
- ❌ Não carrega dados no banco de dados

**Status:** 🔴 **INCOMPLETO - Precisa implementar toda a lógica de ETL e carga no banco**

---

## 📋 Checklist de Requisitos do Professor

| Requisito                                                      | Status      | Observações                            |
| -------------------------------------------------------------- | ----------- | -------------------------------------- |
| ✅ **Backend publicado no Azure (WebApp)**                     | 🟡 Pendente | Código pronto, precisa deploy          |
| ✅ **Frontend publicado no Azure (Static Web App ou Storage)** | 🟡 Pendente | Build pronto, precisa deploy           |
| ✅ **Azure Function Download (Time Trigger)**                  | 🟡 Pendente | Implementado, precisa deploy + ajustes |
| ⚠️ **Azure Function Carga (Blob Trigger)**                     | 🔴 Pendente | Precisa implementar lógica completa    |
| ✅ **Base de dados (PostgreSQL/MySQL/SQL Server)**             | 🟢 OK       | MySQL já criado e configurado          |

**Legenda:**

- 🟢 OK = Completamente pronto
- 🟡 Pendente = Implementado, mas não publicado
- 🔴 Pendente = Precisa desenvolvimento

---

## 🚀 O Que Precisa Ser Feito

### 🔴 **CRÍTICO - Alta Prioridade**

#### 1. **Implementar a Function de Carga (function_load)**

A Azure Function de carga está **incompleta**. É necessário:

**a) Parser do XML da B3**

- Ler o arquivo XML do blob
- Extrair os dados de cotações seguindo o layout oficial da B3
- Mapear campos: código do ativo, data, preço abertura, fechamento, volume, etc.

**b) Conexão com o Banco de Dados**

- Adicionar dependência MySQL/PostgreSQL ao `requirements.txt`
- Implementar conexão com o banco Azure
- Criar lógica de inserção/atualização (upsert)

**c) Tratamento de Erros**

- Validação de dados
- Logging de erros
- Retry em caso de falha

**Código sugerido para `function_load/function_app.py`:**

```python
import azure.functions as func
import logging
import mysql.connector
import os
from lxml import etree

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="dados-pregao-bolsa",
                  connection="AZURESTORAGE_CONNECTION_STRING")
def load_file_b3_trigger(myblob: func.InputStream):
    logging.info(f"Processando arquivo: {myblob.name}")

    # 1. Ler XML
    xml_content = myblob.read()

    # 2. Parsear dados (implementar conforme layout B3)
    assets = parse_b3_xml(xml_content)

    # 3. Carregar no banco
    load_to_database(assets)

    logging.info(f"Carga concluída: {len(assets)} registros")

def parse_b3_xml(xml_content):
    # TODO: Implementar parse conforme layout B3
    pass

def load_to_database(assets):
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()

    for asset in assets:
        # Inserção com ON DUPLICATE KEY UPDATE para evitar duplicatas
        query = """
        INSERT INTO asset (nome, dataPregao, precoAbertura, precoFechamento,
                          volumeDiario, precoMedio)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            precoAbertura = VALUES(precoAbertura),
            precoFechamento = VALUES(precoFechamento),
            volumeDiario = VALUES(volumeDiario),
            precoMedio = VALUES(precoMedio)
        """
        cursor.execute(query, (
            asset['nome'], asset['data'], asset['abertura'],
            asset['fechamento'], asset['volume'], asset['medio']
        ))

    conn.commit()
    cursor.close()
    conn.close()
```

**Adicionar ao `requirements.txt`:**

```
azure-functions
azure-storage-blob
mysql-connector-python
lxml
```

#### 2. **Corrigir Data na Function de Extração**

Arquivo: `function_extract/extract.py` linha ~48

**Problema:** Data está hardcoded como `"251107"`

```python
dt = "251107" #yymmdd(datetime.now())
```

**Solução:**

```python
dt = yymmdd(datetime.now())  # Usar data atual
```

Verificar se a função `yymmdd()` no `helpers.py` está implementada corretamente.

---

### 🟡 **IMPORTANTE - Deploy no Azure**

#### 3. **Publicar Backend no Azure Web App**

**Passos:**

1. Criar um Azure Web App (Linux/Java 21)
2. Configurar variáveis de ambiente no Azure:
   - `SPRING_DATASOURCE_URL`
   - `SPRING_DATASOURCE_USERNAME`
   - `SPRING_DATASOURCE_PASSWORD`
3. Fazer deploy via:
   - Azure CLI: `az webapp deploy`
   - GitHub Actions
   - VS Code Extension (Azure App Service)
   - Maven plugin

**Comando Maven para build:**

```bash
cd "Projeto Cloud/backend"
./mvnw clean package
```

#### 4. **Publicar Frontend no Azure**

**Opção A - Static Web App (Recomendado):**

```bash
# Instalar Azure Static Web Apps CLI
npm install -g @azure/static-web-apps-cli

# Deploy
cd "Projeto Cloud/frontend"
swa deploy ./build
```

**Opção B - Storage Account:**

1. Criar Storage Account
2. Habilitar "Static website"
3. Upload dos arquivos da pasta `build/`
4. Configurar CORS

⚠️ **IMPORTANTE:** Atualizar URL do backend no `api.js` após deploy!

#### 5. **Publicar Azure Functions**

**Para function_extract:**

```bash
cd "Projeto Cloud/function_extract"
func azure functionapp publish <nome-function-app>
```

**Para function_load:**

```bash
cd "Projeto Cloud/function_load"
func azure functionapp publish <nome-function-app>
```

**Configurar no Azure Portal:**

- Application Settings (variáveis de ambiente)
- Connection strings do Storage Account
- Connection string do banco de dados

---

### 🟢 **OPCIONAL - Melhorias**

#### 6. **Segurança**

- ❌ Remover credenciais hardcoded do `application.properties`
- ✅ Migrar para **Azure Key Vault**
- ✅ Usar **Managed Identity** nas Functions

#### 7. **Monitoramento**

- Habilitar Application Insights
- Configurar alertas de erros
- Dashboard de métricas

#### 8. **CI/CD**

- Configurar GitHub Actions para deploy automático
- Pipeline de testes automatizados

#### 9. **Validação de Dados**

- Adicionar validações no backend (Bean Validation)
- Tratamento de erros mais robusto
- Health check endpoints

#### 10. **Performance**

- Adicionar índices no banco de dados (data, nome)
- Cache com Redis
- Otimizar queries

---

## 📊 Fluxo de Dados Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO DO PIPELINE                        │
└─────────────────────────────────────────────────────────────┘

1️⃣ [Timer Trigger - A cada 30s]
   ↓
2️⃣ [Function Extract]
   - Baixa ZIP da B3
   - Extrai arquivos XML
   - Upload para Blob Storage (container: dados-pregao-bolsa)
   ↓
3️⃣ [Blob Trigger - Novo arquivo detectado]
   ↓
4️⃣ [Function Load] ⚠️ PRECISA IMPLEMENTAR
   - Parse do XML
   - Extração de dados de ativos
   - INSERT/UPDATE no MySQL
   ↓
5️⃣ [MySQL Database no Azure]
   - Armazena histórico de cotações
   ↓
6️⃣ [Backend API - Spring Boot]
   - Consulta dados via JPA
   - Disponibiliza endpoints REST
   ↓
7️⃣ [Frontend React]
   - Consome API
   - Exibe dashboards e gráficos
```

---

## 🗂️ Estrutura de Dados

### Tabela: `asset`

```sql
CREATE TABLE asset (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),              -- Código do ativo (ex: PETR4)
    dataPregao DATE,                -- Data do pregão
    precoAbertura DECIMAL(19,4),    -- Preço de abertura
    precoFechamento DECIMAL(19,4),  -- Preço de fechamento
    precoMedio DECIMAL(19,4),       -- Preço médio
    volumeDiario DECIMAL(19,4),     -- Volume negociado

    -- Índices recomendados
    INDEX idx_nome (nome),
    INDEX idx_data (dataPregao),
    UNIQUE KEY uk_nome_data (nome, dataPregao)  -- Evitar duplicatas
);
```

---

## 🔑 Variáveis de Ambiente Necessárias

### Backend (Web App)

```bash
SPRING_DATASOURCE_URL=jdbc:mysql://ativos-b3-ibmec.mysql.database.azure.com/ativosb3
SPRING_DATASOURCE_USERNAME=rcbruz
SPRING_DATASOURCE_PASSWORD=123456#A
```

### Function Extract

```bash
AZURESTORAGE_CONNECTION_STRING=<connection-string>
AZURESTORAGE_CONTAINER_NAME=dados-pregao-bolsa
```

### Function Load

```bash
AZURESTORAGE_CONNECTION_STRING=<connection-string>
DB_HOST=ativos-b3-ibmec.mysql.database.azure.com
DB_USER=rcbruz
DB_PASSWORD=123456#A
DB_NAME=ativosb3
```

### Frontend

```javascript
// src/api.js
baseURL: "<URL-DO-BACKEND-APÓS-DEPLOY>";
```

---

## 📝 Próximos Passos Recomendados

### Fase 1: Completar Implementação (1-2 dias)

1. ✅ Implementar lógica da `function_load`
2. ✅ Corrigir data na `function_extract`
3. ✅ Testar fluxo completo localmente

### Fase 2: Deploy no Azure (1 dia)

4. ✅ Publicar Backend no Web App
5. ✅ Publicar Frontend no Static Web App
6. ✅ Publicar ambas Functions
7. ✅ Configurar variáveis de ambiente

### Fase 3: Testes e Validação (0.5 dia)

8. ✅ Testar fluxo end-to-end
9. ✅ Verificar carga de dados
10. ✅ Validar frontend conectando ao backend

### Fase 4: Documentação (0.5 dia)

11. ✅ Documentar configurações
12. ✅ Criar guia de deploy
13. ✅ Screenshot da solução funcionando

---

## ⚠️ Pontos de Atenção

1. **Credenciais Expostas:** O `application.properties` tem credenciais hardcoded - mover para variáveis de ambiente
2. **Container Blob:** Verificar se o nome do container está consistente (`dados-pregao-bolsa` vs `arquivosb3`)
3. **Layout B3:** Precisa implementar parser seguindo documentação oficial da B3
4. **Timer muito frequente:** 30 segundos pode ser excessivo - considerar ajustar para 1x ao dia
5. **CORS:** Backend aceita todas as origens - restringir em produção

---

## 📚 Recursos Úteis

- [Layout Arquivos B3](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/boletins-diarios/pesquisa-por-pregao/layout-dos-arquivos/)
- [Azure Functions Python](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Static Web Apps](https://learn.microsoft.com/azure/static-web-apps/)
- [Spring Boot on Azure](https://learn.microsoft.com/azure/developer/java/spring-framework/)

---

## ✅ Conclusão

**O projeto está ~70% completo:**

- ✅ Backend funcional
- ✅ Frontend funcional
- ✅ Function de extração funcional
- ⚠️ Function de carga **precisa ser implementada**
- 🔴 Nenhum componente está publicado no Azure ainda

**Tempo estimado para conclusão:** 2-3 dias de trabalho focado.

---

_Documento gerado em: 14/11/2025_
