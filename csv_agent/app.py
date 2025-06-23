import streamlit as st
import os
import shutil
import time
from dotenv import load_dotenv
import sys
# --- MODIFICADO ---
import google.genai as genai

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph import create_graph, AgentState

# ... (Configuração da página inalterada) ...

def run_agent_process(zip_file_path: str, user_question: str) -> dict:
    """Executa o fluxo completo do agente e retorna o estado final."""
    extraction_dir = f"extracted_data_{int(time.time())}"
    # ... (lógica de diretório inalterada) ...
    os.makedirs(extraction_dir)

    try:
        app = create_graph()

        # --- MODIFICADO ---
        # Cria o cliente uma única vez aqui
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

        # Injeta o cliente no estado inicial
        initial_state: AgentState = {
            "user_query": user_question,
            "zip_file_path": zip_file_path,
            "data_directory": extraction_dir,
            "client": client,  # Passa o cliente para o estado
            "available_csv_paths": None,
            "selected_csv_paths": None,
            "dataframe": None,
            "sql_query": None,
            "query_result": None,
            "final_answer": None,
            "error_message": None,
            "error_message_agg": None,
        }

        final_state = app.invoke(initial_state)
        return final_state
    # ... (resto da função inalterado) ...
    except Exception as e:
        return {"final_answer": f"Erro durante execução: {str(e)}"}
    finally:
        # Limpa diretório temporário
        if os.path.exists(extraction_dir):
            shutil.rmtree(extraction_dir)


# ... (O resto da interface `main()` em app.py não precisa de mudanças) ...
def main():
    st.title("🤖 BrxAgente IA Fiscal")
    st.markdown("**Analise seus dados fiscais com Inteligência Artificial**")

    # Verificar se a API key está configurada
    if not os.getenv('GOOGLE_API_KEY'):
        st.error("⚠️ GOOGLE_API_KEY não está configurada. Configure a variável de ambiente antes de usar a aplicação.")
        st.info("Crie um arquivo .env na raiz do projeto com: GOOGLE_API_KEY=sua_chave_aqui")
        return

    # Sidebar para upload
    with st.sidebar:
        st.header("📁 Upload de Arquivos")
        uploaded_file = st.file_uploader(
            "Selecione um arquivo ZIP com CSVs",
            type=['zip'],
            help="Faça upload de um arquivo ZIP contendo arquivos CSV para análise"
        )

        if uploaded_file:
            # Salva arquivo temporariamente
            temp_zip_path = f"temp_{uploaded_file.name}"
            with open(temp_zip_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Arquivo '{uploaded_file.name}' carregado!")
        else:
            temp_zip_path = None

    # Área principal
    st.header("💬 Faça sua Pergunta")
    user_question = st.text_area(
        "Digite sua pergunta sobre os dados:",
        placeholder="Ex: Qual é o total de vendas por fornecedor?",
        height=100
    )

    # Botão de processamento
    if st.button("🚀 Processar", type="primary", disabled=not (temp_zip_path and user_question)):
        if not temp_zip_path:
            st.error("Por favor, faça upload de um arquivo ZIP.")
        elif not user_question.strip():
            st.error("Por favor, digite uma pergunta.")
        else:
            with st.spinner("🔄 Processando sua solicitação..."):
                try:
                    # Executa o processamento
                    result = run_agent_process(temp_zip_path, user_question)

                    # Exibe resultado
                    if result.get("final_answer"):
                        st.success("✅ Processamento concluído!")
                        st.header("📊 Resultado da Análise")
                        st.write(result["final_answer"])
                    else:
                        st.error("❌ Não foi possível processar sua solicitação.")
                        if result.get("error_message"):
                            st.error(f"Erro: {result['error_message']}")

                except Exception as e:
                    st.error(f"❌ Erro durante o processamento: {str(e)}")
                finally:
                    # Remove arquivo temporário
                    if os.path.exists(temp_zip_path):
                        os.remove(temp_zip_path)
if __name__ == "__main__":
    main()