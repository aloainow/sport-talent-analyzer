import streamlit as st
from openai import OpenAI

def get_sport_recommendations(results):
    """
    Analisa os resultados dos testes e sugere esportes adequados.
    """
    try:
        # Inicializa o cliente OpenAI
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Prepara os dados para enviar para a API
        prompt = f"""
        Como especialista em análise esportiva, analise os seguintes resultados de testes:

        Testes de Força:
        - Flexões: {results['força'].get('flexoes', 0)} repetições
        - Abdominais: {results['força'].get('abdominais', 0)} repetições

        Testes de Velocidade:
        - Corrida 20m: {results['velocidade'].get('corrida_20m', 0)} segundos
        - Agilidade: {results['velocidade'].get('agilidade', 0)} segundos

        Testes de Resistência:
        - Burpees: {results['resistencia'].get('burpees', 0)} repetições
        - Cooper 6min: {results['resistencia'].get('cooper', 0)} metros

        Testes de Coordenação:
        - Equilíbrio: {results['coordenacao'].get('equilibrio', 0)} segundos
        - Saltos: {results['coordenacao'].get('saltos', 0)} repetições

        Com base nesses resultados, sugira 5 esportes mais adequados. 
        Para cada esporte, forneça:
        1. Nome do esporte
        2. Porcentagem de compatibilidade (0-100)
        3. Lista de 3 pontos fortes que fazem o candidato adequado para este esporte
        4. Lista de 2 áreas para desenvolvimento

        Retorne no formato JSON exato:
        [
            {{
                "name": "nome do esporte",
                "compatibility": número,
                "strengths": ["ponto forte 1", "ponto forte 2", "ponto forte 3"],
                "development": ["área 1", "área 2"]
            }},
            ...
        ]
        """

        # Faz a chamada para a API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de talentos esportivos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Processa a resposta
        import json
        recommendations = json.loads(response.choices[0].message.content)
        
        # Valida o formato
        for rec in recommendations:
            if not all(key in rec for key in ['name', 'compatibility', 'strengths', 'development']):
                raise ValueError("Formato de resposta inválido")
        
        return recommendations

    except Exception as e:
        st.error(f"Erro ao processar recomendações: {str(e)}")
        return None
