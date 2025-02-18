import streamlit as st
from openai import OpenAI

# Inicialização simplificada do cliente OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"Erro ao inicializar cliente OpenAI: {str(e)}")
    raise

def get_sport_recommendations(user_data):
    try:
        # Seu código de recomendação aqui
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sports talent analyzer."},
                {"role": "user", "content": f"Based on this data: {user_data}, what sports would you recommend?"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao obter recomendações: {str(e)}")
        return None
