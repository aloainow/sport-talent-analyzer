import streamlit as st
import json
import os
from openai import OpenAI

def get_sport_recommendations(scores):
    """
    Gera recomendações de esportes usando a API do OpenAI baseado nos scores do atleta
    """
    try:
        # Verifica se a chave da API está configurada
        if "OPENAI_API_KEY" not in st.secrets:
            st.error("Chave da API OpenAI não encontrada!")
            return []
        
        # Configura o cliente OpenAI com apenas a API key
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Prepara o prompt
        prompt = f"""
        Atue como um especialista em identificação de talentos esportivos. 
        Analise o perfil do atleta com base nos seguintes scores (0-100):
        
        - Dados Físicos: {scores.get('dados_fisicos', 0)}
        - Habilidades Técnicas: {scores.get('habilidades_tecnicas', 0)}
        - Aspectos Táticos: {scores.get('aspectos_taticos', 0)}
        - Fatores Psicológicos: {scores.get('fatores_psicologicos', 0)}
        
        Forneça um JSON com as 5 modalidades esportivas mais compatíveis neste formato:
        [
            {{
                "name": "Nome do Esporte",
                "compatibility": 85,
                "strengths": ["ponto forte 1", "ponto forte 2"],
                "development": ["área 1", "área 2"]
            }}
        ]
        Retorne APENAS o JSON, sem texto adicional.
        """
        
        # Faz a chamada à API
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Processa e valida a resposta
        content = response.choices[0].message.content.strip()
        try:
            recommendations = json.loads(content)
            if not isinstance(recommendations, list):
                raise ValueError("Resposta inválida: não é uma lista")
            return recommendations
        except json.JSONDecodeError as e:
            st.error(f"Erro ao processar JSON da resposta: {str(e)}")
            return []
            
    except Exception as e:
        st.error(f"Erro ao gerar recomendações: {str(e)}")
        return []
