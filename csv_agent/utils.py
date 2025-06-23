# -*- coding: utf-8 -*-
import os
import zipfile
import pandas as pd
from typing import List
from functools import reduce


def unzip_file(zip_path: str, extract_to: str) -> bool:
    """Descompacta um arquivo ZIP para um diretório específico."""
    try:
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Arquivo '{zip_path}' descompactado em '{extract_to}'")
        return True
    except Exception as e:
        print(f"Erro ao descompactar '{zip_path}': {e}")
        return False


def find_csv_files(directory: str) -> List[str]:
    """Encontra todos os arquivos CSV em um diretório e seus subdiretórios."""
    csv_files = []
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.csv'):
                    csv_files.append(os.path.join(root, file))
        print(f"Encontrados {len(csv_files)} arquivos CSV em '{directory}'")
        return csv_files
    except Exception as e:
        print(f"Erro ao buscar arquivos CSV em '{directory}': {e}")
        return []


# --- MODIFICADO ---
# Nova função para fazer o merge dos DataFrames
def merge_dataframes(dataframes: List[pd.DataFrame], merge_key: str) -> pd.DataFrame:
    """
    Faz o merge de uma lista de DataFrames usando uma chave comum.
    Args:
        dataframes (List[pd.DataFrame]): Lista de DataFrames para unir.
        merge_key (str): Nome da coluna usada como chave para o merge.
    Returns:
        pd.DataFrame: DataFrame único resultante do merge.
    """
    if not dataframes:
        return pd.DataFrame()
    if len(dataframes) == 1:
        return dataframes[0]

    # Usa reduce para aplicar o merge de forma sequencial na lista de dataframes
    # O merge 'outer' garante que todos os dados de todos os arquivos sejam mantidos
    merged_df = reduce(lambda left, right: pd.merge(left, right, on=merge_key, how='outer'), dataframes)
    print(f"DataFrames unidos pela chave '{merge_key}'. Shape final: {merged_df.shape}")
    return merged_df