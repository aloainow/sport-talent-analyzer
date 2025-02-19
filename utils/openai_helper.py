import streamlit as st
import json
import os
from importlib import import_module

def get_recommendations_without_api():
    """Retorna recomendações padrão caso haja problema com a API"""
    return [
        {
            "name": "Natação",
            "compatibility": 85,
            "strengths": ["Condicionamento físico geral", "Baixo impacto"],
            "development": ["Técnica específica"]
        },
        {
            "name": "Corrida",
            "compatibility": 80,
            "strengths": ["Resistência cardiovascular", "Acessibilidade"],
            "development": ["Força muscular"]
        },
        {
            "name": "Ciclismo",
            "compatibility": 75,
            "strengths": ["Resistência", "Baixo impacto articular"],
            "development": ["Equilíbrio"]
        },
        {
            "name": "Musculação",
            "compatibility": 70,
            "strengths": ["Força muscular", "Controle motor"],
            "development": ["Flexibilidade"]
        },
        {
            "name": "Yoga",
            "compatibility": 65,
            "strengths": ["Flexibilidade", "Equilíbrio"],
            "development": ["Força explosiva"]
        }
    ]

def create_openai_client():
    """Cria um cliente OpenAI com configuração mínima"""
    try:
        OpenAI = import_module('openai').OpenAI
        http_client = import_module('openai.http_client').HttpClient
        
        # Força a configuração mínima do cliente HTTP
        minimal_http_client = http_client(
            base_url="https://api.openai.com/v1",
            timeout=60.0,
            max_retries=2
        )
        
        # Cria o cliente OpenAI com o cliente HTTP personalizado
        return OpenAI(
            api_key=st.secrets["OPENAI_API_KEY"],
            http_client=minimal_http_client
        )
    except Exception as e:
        st.warning(f"Erro ao criar cliente OpenAI: {str(e)}")
        return None

def get_sport_recommendations(scores):
    """
    Gera recomendações de esportes usando a API do OpenAI baseado nos scores do atleta
    """
    try:
        if "OPENAI_API_KEY" not in st.secrets:
            st.warning("Chave da API OpenAI não encontrada. Usando recomendações padrão.")
            return get_recommendations_without_api()

        client = create_openai_client()
        if client is None:
            return get_recommendations_without_api()

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

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            recommendations = json.loads(content)
            
            if isinstance(recommendations, list) and len(recommendations) > 0:
                return recommendations
            else:
                st.warning("Resposta da API inválida. Usando recomendações padrão.")
                return get_recommendations_without_api()
                
        except Exception as e:
            st.warning(f"Erro ao processar recomendações da API. Usando recomendações padrão. Erro: {str(e)}")
            return get_recommendations_without_api()
            
    except Exception as e:
        st.warning(f"Erro inesperado. Usando recomendações padrão. Erro: {str(e)}")
        return get_recommendations_without_api()
