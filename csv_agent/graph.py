from typing import TypedDict, Optional, Any, List, Annotated
import operator
import pandas as pd
from langgraph.graph import StateGraph, END
# --- MODIFICADO ---
# Importa o tipo Client para usar na definição do estado
from google.genai.client import Client

from agents import (
    file_manager_agent,
    file_selector_agent,
    data_loader_agent,
    query_agent,
    response_generator_agent
)

# --- MODIFICADO ---
# Definição do Estado do Grafo com o client
class AgentState(TypedDict):
    user_query: str
    zip_file_path: Optional[str]
    data_directory: str
    client: Client  # Adiciona o cliente da API ao estado
    available_csv_paths: Optional[List[str]]
    selected_csv_paths: Optional[List[str]]
    dataframe: Optional[pd.DataFrame]
    sql_query: Optional[str]
    query_result: Optional[str]
    final_answer: Optional[str]
    error_message: Optional[str]
    error_message_agg: Annotated[Optional[List[str]], operator.add]


def create_graph():
    """
    Cria e configura o grafo com o fluxo otimizado.
    """
    workflow = StateGraph(AgentState)

    # Nós e conexões permanecem os mesmos
    workflow.add_node("file_manager", file_manager_agent)
    workflow.add_node("file_selector", file_selector_agent)
    workflow.add_node("data_loader", data_loader_agent)
    workflow.add_node("query_executor", query_agent)
    workflow.add_node("response_generator", response_generator_agent)

    workflow.set_entry_point("file_manager")
    workflow.add_edge("file_manager", "file_selector")
    workflow.add_edge("file_selector", "data_loader")
    workflow.add_edge("data_loader", "query_executor")
    workflow.add_edge("query_executor", "response_generator")
    workflow.add_edge("response_generator", END)

    return workflow.compile()