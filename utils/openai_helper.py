import streamlit as st
from openai import OpenAI

def get_sport_recommendations(user_data):
    """Obtém recomendações de esportes baseadas nos dados do usuário"""
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sports talent analyzer."},
                {"role": "user", "content": f"Based on this data: {user_data}, what sports would you recommend?"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Erro ao obter recomendações: {str(e)}")
        return None
