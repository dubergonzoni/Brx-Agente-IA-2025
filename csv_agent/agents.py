import os
import pandas as pd
from typing import Dict, Any, List
import duckdb

import google.genai as genai
from google.genai import types

from utils import unzip_file, find_csv_files, merge_dataframes

MERGE_KEY = "CHAVE DE ACESSO"


def get_genai_client():
    """Obtém o cliente GenAI configurado."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY não está definida nas variáveis de ambiente")
    return genai.Client(api_key=api_key)


# Os agentes file_manager, file_selector e data_loader permanecem inalterados
def file_manager_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- Executando Agente Gerenciador de Arquivos ---")
    zip_file_path = state.get("zip_file_path")
    data_directory = state.get("data_directory")

    if not data_directory:
        return {"error_message": "Diretório de dados não especificado."}

    if zip_file_path and os.path.exists(zip_file_path):
        if not unzip_file(zip_file_path, data_directory):
            return {"error_message": f"Falha ao descompactar {zip_file_path}."}

    available_csv_paths = find_csv_files(data_directory)

    if not available_csv_paths:
        return {"error_message": "Nenhum arquivo CSV encontrado no diretório."}

    print(f"Arquivos CSV encontrados: {available_csv_paths}")
    return {"available_csv_paths": available_csv_paths}


def file_selector_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- Executando Agente Seletor de Arquivos ---")
    available_csv_paths = state.get("available_csv_paths", [])
    if not available_csv_paths:
        return {"error_message": "Nenhum arquivo CSV disponível para seleção."}
    print(f"Arquivos CSV selecionados: {available_csv_paths}")
    return {"selected_csv_paths": available_csv_paths}


def data_loader_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Agente que carrega os CSVs e faz o merge em um único DataFrame Pandas."""
    print("--- Executando Agente Carregador e Unificador de Dados ---")
    selected_csv_paths = state.get("selected_csv_paths", [])
    if not selected_csv_paths:
        return {"error_message": "Nenhum arquivo CSV selecionado para carregar."}

    try:
        # Carrega os dataframes
        dataframes = [pd.read_csv(csv_path) for csv_path in selected_csv_paths]

        # Validação para garantir que a chave de merge existe em todos os dataframes
        for i, df in enumerate(dataframes):
            if MERGE_KEY not in df.columns:
                error_msg = f"A chave de merge '{MERGE_KEY}' não foi encontrada no arquivo '{os.path.basename(selected_csv_paths[i])}'."
                print(f"❌ {error_msg}")
                return {"error_message": error_msg}

        # Une os dataframes
        merged_df = merge_dataframes(dataframes, MERGE_KEY)

        if merged_df.empty:
            return {
                "error_message": f"Merge resultou em um DataFrame vazio. Verifique a chave '{MERGE_KEY}' e o conteúdo dos arquivos."}

        print(f"DataFrame final criado com {merged_df.shape[0]} linhas e {merged_df.shape[1]} colunas.")
        # Garante que o dataframe seja retornado para o estado
        return {"dataframe": merged_df}

    except Exception as e:
        error_msg = f"Erro ao carregar ou unificar dados: {e}"
        print(f"❌ {error_msg}")
        return {"error_message": error_msg}


def query_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Agente que gera uma consulta SQL e a executa no DataFrame usando DuckDB."""
    print("--- Executando Agente de Consulta SQL com DuckDB ---")
    user_query = state.get("user_query", "")
    dataframe = state.get("dataframe")
    client = state.get("client")

    if dataframe is None or client is None:
        return {"error_message": "DataFrame ou cliente da API não disponível para consulta."}

    try:
        df_name = "fiscal_data"
        locals()[df_name] = dataframe

        schema = dataframe.dtypes.to_string()
        schema_info = f"You can query the pandas DataFrame named `{df_name}`.\nColumns (and types):\n{schema}"

        # --- MODIFICADO --- Adicionada instrução sobre a regra do GROUP BY
        prompt = f"""You are a SQL expert. Your task is to generate a single, executable SQL query to answer the user's question based on the provided DataFrame schema.

User Query: "{user_query}"

DataFrame Schema:
{schema_info}

Guidelines:
- Write a single SQL query that works with DuckDB.
- **`GROUP BY` Rule:** Any column in the `SELECT` list must either be in the `GROUP BY` clause or be used in an aggregate function (like `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`).
- If you need to perform date functions (like strftime) on a column that is a STRING/VARCHAR, you MUST first cast it to a DATE. For dates in 'YYYY-MM-DD' format, use `CAST("column_name" AS DATE)`.
- Do NOT use a `LIMIT` clause unless the user explicitly asks for a specific number of results (e.g., "top 5", "the 10 biggest"). Return all relevant results ordered appropriately.
- Do NOT provide any explanation, preamble, or markdown formatting.
- Your entire response must be ONLY the SQL query.
- If you cannot generate a query, respond with 'ERROR'.

Return ONLY the SQL query or 'ERROR'."""

        config = types.GenerateContentConfig(
            temperature=0.0,
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )

        sql_query = response.text.strip().replace("```sql", "").replace("```", "")
        print(f"Consulta SQL gerada: \n{sql_query}")

        sanitized_query = sql_query.strip().upper()
        if not (sanitized_query.startswith('SELECT') or sanitized_query.startswith('WITH')):
            print("❌ Falha na geração de SQL: A resposta do modelo não é uma consulta SQL válida.")
            error_msg = f"O modelo de IA não conseguiu gerar uma consulta SQL válida para a sua pergunta. Resposta recebida: '{sql_query}'"
            return {"error_message": error_msg}

        print("Executando a consulta com DuckDB...")
        con = duckdb.connect()
        result_df = con.execute(sql_query).fetchdf()

        print("Resultado da consulta obtido:")
        print(result_df.to_string())

        return {"sql_query": sql_query, "query_result": result_df.to_string()}

    except Exception as e:
        return {"error_message": f"Erro na geração ou execução da consulta com DuckDB: {e}"}


def response_generator_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Agente que gera a resposta final formatada."""
    print("--- Executando Agente Gerador de Resposta ---")
    query_result = state.get("query_result")
    user_query = state.get("user_query", "")
    sql_query = state.get("sql_query", "N/A")
    client = state.get("client")

    if state.get("error_message"):
        return {"final_answer": f"Ocorreu um erro: {state['error_message']}"}

    if not query_result or client is None:
        return {"final_answer": "Não foi possível processar a consulta."}

    try:
        config = types.GenerateContentConfig(
            temperature=0.1,
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )

        prompt = f"""You are a helpful data analyst assistant.
Your goal is to provide a clear and professional final answer in Brazilian Portuguese based on the data retrieved from a query.
Original User Query: "{user_query}"
Executed SQL Query: {sql_query}
Data Result:
{query_result}
Task:
Format a final response in Brazilian Portuguese that:
1. Directly answers the user's question.
2. Is well-structured and clear.
3. Includes specific numbers from the "Data Result" to support the analysis.
4. If the result is a table, summarize the key findings. Do not just repeat the table.
Generate ONLY the final response to the user."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )

        return {"final_answer": response.text}

    except Exception as e:
        return {"final_answer": f"Erro ao gerar resposta final: {e}"}