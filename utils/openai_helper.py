import streamlit as st
import json
import openai

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

def get_sport_recommendations(scores):
    """
    Gera recomendações de esportes usando a API do OpenAI baseado nos scores do atleta
    """
    try:
        if "OPENAI_API_KEY" not in st.secrets:
            st.warning("Chave da API OpenAI não encontrada. Usando recomendações padrão.")
            return get_recommendations_without_api()

        # Configura a API key
        openai.api_key = st.secrets["OPENAI_API_KEY"]

        # Ajusta o prompt para forçar uma resposta JSON válida
        prompt = f"""
Analise o perfil do atleta com os seguintes scores (de 0 a 100) em atributos individuais e retorne APENAS um JSON válido com as 5 modalidades esportivas mais compatíveis.

- Velocidade: {scores.get('velocidade', 0)}
- Força Superior: {scores.get('forca_superior', 0)}
- Força Inferior: {scores.get('forca_inferior', 0)}
- Coordenação: {scores.get('coordenacao', 0)}
- Precisão: {scores.get('precisao', 0)}
- Agilidade: {scores.get('agilidade', 0)}
- Equilíbrio: {scores.get('equilibrio', 0)}
- Tomada de Decisão: {scores.get('tomada_decisao', 0)}
- Visão de Jogo: {scores.get('visao_jogo', 0)}
- Posicionamento: {scores.get('posicionamento', 0)}
- Motivação: {scores.get('motivacao', 0)}
- Resiliência: {scores.get('resiliencia', 0)}
- Trabalho em Equipe: {scores.get('trabalho_equipe', 0)}
- Altura: {scores.get('altura', 0)}
- Peso: {scores.get('peso', 0)}
- Envergadura: {scores.get('envergadura', 0)}

        O JSON deve seguir EXATAMENTE este formato, sem texto adicional:
        [
            {{
                "name": "Nome do Esporte",
                "compatibility": 85,
                "strengths": ["ponto forte 1", "ponto forte 2"],
                "development": ["área 1", "área 2"]
            }}
        ]
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Mudando para gpt-3.5-turbo que é mais estável
                messages=[
                    {"role": "system", "content": "Você é um especialista em identificação de talentos esportivos. Responda apenas com JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
                        
            content = response.choices[0].message.content.strip()
            
            # Tenta encontrar JSON válido na resposta
            try:
                # Remove qualquer texto antes e depois dos colchetes
                json_start = content.find("[")
                json_end = content.rfind("]") + 1
                if json_start >= 0 and json_end > json_start:
                    content = content[json_start:json_end]
                
                recommendations = json.loads(content)
                
                if isinstance(recommendations, list) and len(recommendations) > 0:
                    return recommendations
                else:
                    st.warning("Formato de resposta inválido. Usando recomendações padrão.")
                    return get_recommendations_without_api()
                    
            except json.JSONDecodeError as e:
                st.warning(f"Erro ao processar JSON da resposta: {str(e)}")
                st.write("Debug - Conteúdo que causou erro:", content)
                return get_recommendations_without_api()
                
        except Exception as e:
            st.warning(f"Erro ao processar recomendações da API: {str(e)}")
            return get_recommendations_without_api()
            
    except Exception as e:
        st.warning(f"Erro inesperado: {str(e)}")
        return get_recommendations_without_api()
