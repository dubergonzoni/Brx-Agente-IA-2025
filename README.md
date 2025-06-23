# Brx-Agente-IA-2025
Grupo de trabalho para realização dos desafios referentes ao curso Agentes Autônomos com Redes Generativas, através de uma parceria entre o Institut d'Intelligence Artificielle Appliquée (I2A2) e a empresa Meta/Metadatah.

# BrxAgenteIA2025 Desafio2 - Agentes Autônomos: Análise de CSV

**Este módulo do BrxAgenteIA2025** é uma aplicação de Inteligência Artificial desenvolvida para resolver o desafio proposto para analisar dados fiscais a partir de arquivos CSV contidos em um arquivo ZIP. O sistema utiliza uma arquitetura de agentes, orquestrada pelo LangGraph, para interpretar perguntas em linguagem natural, gerar e executar consultas SQL em tempo real, e fornecer respostas analíticas claras e objetivas.

## Funcionalidades

  - **Processamento de Arquivos ZIP:** Extrai e processa múltiplos arquivos CSV de um único arquivo ZIP.
  - **Unificação de Dados:** Realiza o `merge` inteligente de diferentes arquivos CSV utilizando uma chave primária comum (`CHAVE DE ACESSO`).
  - **Consultas em Linguagem Natural:** Permite que o usuário faça perguntas complexas em português.
  - **Geração Dinâmica de SQL:** Um agente de IA traduz a pergunta do usuário para uma consulta SQL precisa.
  - **Execução em Memória:** Utiliza o DuckDB para executar as consultas SQL diretamente no DataFrame unificado, garantindo alta performance sem a necessidade de um banco de dados externo.
  - **Respostas Analíticas:** Um segundo agente de IA analisa os resultados da consulta e gera uma resposta final bem estruturada para o usuário.
  - **Interface Web Interativa:** Possui uma interface web, construída com Streamlit, para uma experiência de uso amigável.

## Tecnologias Utilizadas

  - **Python 3.9+**
  - **LangGraph:** Framework principal para orquestrar o fluxo de múltiplos agentes e gerenciar o estado da aplicação.
  - **Google Gemini (via `google-genai`):** Modelo de linguagem utilizado para a geração de SQL e de respostas em linguagem natural.
  - **Pandas:** Para carregamento, manipulação e unificação dos dados a partir dos arquivos CSV.
  - **DuckDB:** Motor de banco de dados analítico (OLAP) em memória, para execução de consultas SQL.
  - **Streamlit:** Para a criação da interface web interativa (`app.py`).

## Configuração do Ambiente

Antes de executar a aplicação, é necessário entrar na pasta csv_agent e configurar o ambiente de desenvolvimento.

### 1\. Pré-requisitos

  - Python 3.9 ou superior instalado.
  - Acesso a uma chave de API do Google Gemini.

### 2\. Instalação das Dependências

Clone este repositório e, na pasta csv_agent do projeto, instale todas as bibliotecas necessárias executando o seguinte comando no seu terminal:

```bash
pip install -r requirements.txt
```

### 3\. Variáveis de Ambiente

A aplicação requer uma chave de API do Google para funcionar. Crie um arquivo chamado `.env` na raiz do projeto e adicione sua chave nele.

**Arquivo `.env`:**

```
GOOGLE_API_KEY="SUA_CHAVE_DE_API_AQUI"
```

## Como Executar a Aplicação Web (`app.py`)

A interface web permite que qualquer usuário interaja com o agente de forma visual e intuitiva, fazendo upload de arquivos e recebendo as análises diretamente no navegador.

**Passo 1: Iniciar o Servidor Streamlit**

Abra um terminal na pasta raiz do projeto e execute o seguinte comando:

```bash
streamlit run app.py
```

**Passo 2: Abrir a Aplicação no Navegador**

Após executar o comando, o Streamlit iniciará um servidor local e exibirá as URLs de acesso no terminal. Geralmente, ele abrirá automaticamente uma aba no seu navegador padrão.

```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.10:8501
```

Acesse a `Local URL` (normalmente `http://localhost:8501`).

**Passo 3: Utilizar a Interface**

A interface web é dividida em duas partes principais:

1.  **Barra Lateral (Sidebar) para Upload:**

      - Clique no botão "**Procurar arquivos**" ou arraste e solte o seu arquivo `.zip` contendo os CSVs fiscais.
      - Aguarde a mensagem de sucesso `✅ Arquivo 'seu_arquivo.zip' carregado!`.

2.  **Área Principal para Perguntas:**

      - Na caixa de texto "**Digite sua pergunta sobre os dados:**", escreva sua análise em português.
      - Clique no botão azul "**🚀 Processar**".

**Passo 4: Analisar o Resultado**

Aguarde o processamento. A aplicação exibirá a resposta final gerada pela IA, e também a consulta SQL que foi executada, para fins de transparência e depuração.

-----

## Execução via Linha de Comando (`main.py`)

Para desenvolvedores ou para execução em lote, a aplicação também pode ser utilizada diretamente pelo terminal. Diferente da versão web, esta abordagem requer que um arquivo específico já esteja presente na pasta do projeto.

**Passo 1: Prepare o Arquivo**

  - **Obrigatório:** Coloque o seu arquivo de dados na **pasta raiz do projeto**.
  - **Nome Exato:** O arquivo precisa ser nomeado **exatamente** como `202401_NFs.zip`. O script `main.py` está configurado para procurar por este nome de arquivo específico e não funcionará com outro.

**Passo 2: Execute o Script**

No terminal, na raiz do projeto, execute:

```bash
python main.py
```

**Passo 3: Interaja no Terminal**

O programa solicitará que você digite a sua pergunta diretamente no console. Após o processamento, a consulta SQL e a resposta final serão impressas no próprio terminal.
