import streamlit as st
import json
from openai import OpenAI

def create_openai_client():
    """
    Cria uma instância do cliente OpenAI com configuração mínima
    """
    try:
        if "OPENAI_API_KEY" not in st.secrets:
            raise ValueError("Chave da API OpenAI não encontrada!")
        
        # Criando cliente com configuração mínima
        return OpenAI(
            api_key=st.secrets["OPENAI_API_KEY"],
            base_url="https://api.openai.com/v1"  # URL base explícita
        )
    except Exception as e:
        st.error(f"Erro ao criar cliente OpenAI: {str(e)}")
        return None

def get_sport_recommendations(scores):
    """
    Gera recomendações de esportes usando a API do OpenAI baseado nos scores do atleta
    """
    try:
        # Cria o cliente OpenAI
        client = create_openai_client()
        if client is None:
            return []
        
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
        
        # Faz a chamada à API com configuração mínima
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
