import os
import shutil
from dotenv import load_dotenv
import google.genai as genai

# Carrega variáveis de ambiente
load_dotenv()

# Importa as funções e o estado do grafo
from graph import create_graph, AgentState


# --- MODIFICADO ---
# A função create_dummy_zip_if_needed foi removida.

def main():
    """Função principal para executar o agente."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY não está configurada.")
        print("Crie um arquivo .env com a seguinte variável:")
        print("GOOGLE_API_KEY='sua_chave_google'")
        return

    # --- MODIFICADO ---
    # O nome do arquivo agora é fixo e verificamos se ele existe.
    zip_file_path = "202401_NFs.zip"
    if not os.path.exists(zip_file_path):
        print(f"❌ Erro: O arquivo '{zip_file_path}' não foi encontrado.")
        print("Por favor, certifique-se de que o arquivo ZIP está na raiz do projeto.")
        return

    # Pergunta do usuário
    user_query = input("\n💬 Digite sua pergunta sobre os dados: ")
    if not user_query.strip():
        print("❌ Pergunta não pode estar vazia.")
        return

    # Diretório de extração
    extraction_directory = "extracted_data"
    if os.path.exists(extraction_directory):
        shutil.rmtree(extraction_directory)

    try:
        print("\n🚀 Iniciando processamento...")
        app = create_graph()

        # Cria o cliente da API uma única vez
        client = genai.Client(api_key=api_key)

        # Define o estado inicial, passando o cliente
        initial_state: AgentState = {
            "user_query": user_query,
            "zip_file_path": zip_file_path,
            "data_directory": extraction_directory,
            "client": client,
            "available_csv_paths": None,
            "selected_csv_paths": None,
            "dataframe": None,
            "sql_query": None,
            "query_result": None,
            "final_answer": None,
            "error_message": None,
            "error_message_agg": None,
        }

        # Executa o workflow
        final_state = app.invoke(initial_state)

        # Exibe resultado
        print("\n" + "=" * 50)
        print("📊 RESULTADO DA ANÁLISE")
        print("=" * 50)

        if final_state.get("sql_query"):
            print(f"🔍 Consulta SQL Executada:\n{final_state['sql_query']}\n")
            print("-" * 50)

        if final_state.get("final_answer"):
            print(final_state["final_answer"])
        else:
            print("❌ Não foi possível processar sua consulta.")
            if final_state.get("error_message"):
                print(f"Erro: {final_state['error_message']}")

        print("=" * 50)

    except Exception as e:
        print(f"❌ Erro durante execução: {str(e)}")

    finally:
        # Limpeza
        if os.path.exists(extraction_directory):
            shutil.rmtree(extraction_directory)
        print("\n🧹 Limpeza concluída.")


if __name__ == "__main__":
    main()