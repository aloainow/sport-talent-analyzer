from openai import OpenAI
import json
import streamlit as st

# Inicializa o cliente OpenAI usando o secret do Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_sport_recommendations(test_results):
    """
    Obtém recomendações de esportes baseadas nos resultados dos testes usando a API da OpenAI.
    """
    # Criar o prompt para a API
    prompt = f"""
    Com base nos seguintes resultados de testes esportivos, recomende os 5 esportes mais adequados para o atleta.
    Os resultados estão em uma escala de 0-10:

    Resultados Físicos:
    {json.dumps(test_results['physical'], indent=2)}

    Resultados Técnicos:
    {json.dumps(test_results['technical'], indent=2)}

    Resultados Táticos:
    {json.dumps(test_results['tactical'], indent=2)}

    Resultados Psicológicos:
    {json.dumps(test_results['psychological'], indent=2)}

    Forneça as recomendações no seguinte formato JSON:
    [
        {{
            "name": "Nome do Esporte",
            "compatibility": percentual de compatibilidade (0-100),
            "strengths": ["ponto forte 1", "ponto forte 2", ...],
            "development": ["área para desenvolver 1", "área para desenvolver 2", ...]
        }},
        ...
    ]

    Considere as características específicas de cada esporte e como elas se alinham com o perfil do atleta.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um especialista em análise esportiva e desenvolvimento de talentos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extrair e processar a resposta
        recommendations = json.loads(response.choices[0].message.content)
        return recommendations

    except Exception as e:
        st.error(f"Erro ao obter recomendações: {str(e)}")
        return []
