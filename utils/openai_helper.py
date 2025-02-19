from openai import OpenAI
import json
import os

def get_sport_recommendations(scores):
    """
    Gera recomendações de esportes usando a API do OpenAI baseado nos scores do atleta
    """
    # Inicializa o cliente OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Criar o prompt para o GPT com os scores e contexto
    prompt = f"""
    Atue como um especialista em identificação de talentos esportivos. 
    Analise o perfil do atleta com base nos seguintes scores (0-100):
    
    - Dados Físicos: {scores['dados_fisicos']}
    - Habilidades Técnicas: {scores['habilidades_tecnicas']}
    - Aspectos Táticos: {scores['aspectos_taticos']}
    - Fatores Psicológicos: {scores['fatores_psicologicos']}
    
    Retorne as 5 modalidades esportivas mais compatíveis em formato JSON com a seguinte estrutura:
    [
        {{
            "name": "Nome do Esporte",
            "compatibility": percentual de compatibilidade (0-100),
            "strengths": ["ponto forte 1", "ponto forte 2"],
            "development": ["área para desenvolvimento 1", "área para desenvolvimento 2"]
        }}
    ]
    
    Considere:
    1. Basear as recomendações nos scores fornecidos
    2. Incluir esportes individuais e coletivos
    3. Considerar o perfil completo do atleta
    4. Fornecer pontos fortes relevantes e áreas específicas para desenvolvimento
    5. Calcular a compatibilidade com base na proximidade dos requisitos do esporte
    
    Retorne APENAS o JSON, sem explicações adicionais.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extrair e parsear o JSON da resposta
        recommendations = json.loads(response.choices[0].message.content)
        return recommendations
        
    except Exception as e:
        print(f"Erro ao gerar recomendações: {str(e)}")
        return []
