import streamlit as st
from openai import OpenAI

# Inicialização básica do cliente OpenAI
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

def get_sport_recommendations(user_data):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sports talent analyzer."},
                {"role": "user", "content": f"Based on this data: {user_data}, what sports would you recommend?"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro na API OpenAI: {str(e)}")
        return None
