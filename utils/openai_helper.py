import streamlit as st
from openai import OpenAI
import os

def initialize_openai_client():
    try:
        # Tenta primeiro pegar a chave das secrets do Streamlit
        api_key = st.secrets.get("OPENAI_API_KEY")
        
        # Se não encontrar nas secrets, tenta pegar das variáveis de ambiente
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        # Se ainda não encontrou a chave, lança um erro
        if not api_key:
            st.error("API Key da OpenAI não encontrada. Por favor, configure nas secrets do Streamlit.")
            raise ValueError("OpenAI API Key não encontrada")
            
        # Inicializa o cliente com a chave encontrada
        return OpenAI(api_key=api_key)
        
    except Exception as e:
        st.error(f"Erro ao inicializar cliente OpenAI: {str(e)}")
        raise

# Inicializa o cliente
client = initialize_openai_client()

def get_sport_recommendations(user_data):
    try:
        # Seu código existente aqui
        pass
    except Exception as e:
        st.error(f"Erro ao obter recomendações: {str(e)}")
        return None
