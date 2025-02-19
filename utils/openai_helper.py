from openai import OpenAI
import os

def get_sport_recommendations(processed_results):
    """
    Gera recomendações de esportes baseadas nos resultados dos testes físicos
    """
    try:
        # Inicializa o cliente OpenAI sem proxy
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Prepara o prompt com os resultados processados
        prompt = criar_prompt_analise(processed_results)
        
        # Faz a chamada para a API do OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """Você é um especialista em análise de aptidão física e recomendação de esportes.
                 Analise os resultados dos testes físicos e recomende os esportes mais adequados baseado no perfil do atleta.
                 Forneça uma análise detalhada incluindo pontos fortes e áreas para desenvolvimento."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Processa a resposta para o formato esperado
        return processar_resposta_openai(response.choices[0].message.content)
    except Exception as e:
        print(f"Erro ao gerar recomendações: {str(e)}")
        # Retorna recomendações padrão em caso de erro
        return get_default_recommendations()
        
def criar_prompt_analise(results):
    """
    Cria o prompt para a análise dos resultados
    """
    prompt = "Com base nos seguintes resultados de testes físicos:\n\n"
    
    # Adiciona resultados de força se disponíveis
    if 'physical' in results:
        força = results['physical']
        prompt += f"Força:\n"
        prompt += f"- Média geral: {força.get('average', 0)}/10\n"
        prompt += f"- Flexões: {força.get('flexoes', 0)}/10\n"
        prompt += f"- Abdominais: {força.get('abdominais', 0)}/10\n\n"
    
    # Adiciona resultados de velocidade se disponíveis
    if 'speed' in results:
        velocidade = results['speed']
        prompt += f"Velocidade:\n"
        prompt += f"- Média geral: {velocidade.get('average', 0)}/10\n"
        prompt += f"- Corrida 20m: {velocidade.get('corrida_20m', 0)}/10\n"
        prompt += f"- Agilidade: {velocidade.get('agilidade', 0)}/10\n\n"
    
    # Adiciona resultados de resistência se disponíveis
    if 'endurance' in results:
        resistencia = results['endurance']
        prompt += f"Resistência:\n"
        prompt += f"- Média geral: {resistencia.get('average', 0)}/10\n"
        prompt += f"- Burpees: {resistencia.get('burpees', 0)}/10\n"
        prompt += f"- Cooper: {resistencia.get('cooper', 0)}/10\n\n"
    
    # Adiciona resultados de coordenação se disponíveis
    if 'coordination' in results:
        coordenacao = results['coordination']
        prompt += f"Coordenação:\n"
        prompt += f"- Média geral: {coordenacao.get('average', 0)}/10\n"
        prompt += f"- Equilíbrio: {coordenacao.get('equilibrio', 0)}/10\n"
        prompt += f"- Saltos: {coordenacao.get('saltos', 0)}/10\n\n"
    
    prompt += """Por favor, forneça:
    1. Os 3 esportes mais recomendados
    2. Para cada esporte:
       - Porcentagem de compatibilidade
       - Pontos fortes que favorecem este esporte
       - Áreas que precisam ser desenvolvidas
    Formate a resposta de forma estruturada para fácil processamento."""
    
    return prompt

def processar_resposta_openai(resposta):
    """
    Processa a resposta do OpenAI para o formato esperado pela aplicação
    """
    try:
        # Este é um processamento simplificado. 
        # Você pode melhorar isto para um parsing mais robusto da resposta
        recomendacoes = []
        
        # Divide a resposta em linhas e processa cada esporte
        linhas = resposta.split('\n')
        esporte_atual = None
        
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
            
            if 'Esporte:' in linha or 'esporte:' in linha:
                if esporte_atual:
                    recomendacoes.append(esporte_atual)
                esporte_atual = {
                    'name': linha.split(':')[1].strip(),
                    'compatibility': 0,
                    'strengths': [],
                    'development': []
                }
            elif 'Compatibilidade:' in linha or 'compatibilidade:' in linha:
                try:
                    comp = int(linha.split(':')[1].strip().replace('%', ''))
                    if esporte_atual:
                        esporte_atual['compatibility'] = comp
                except:
                    pass
            elif 'Pontos fortes:' in linha or 'pontos fortes:' in linha:
                if esporte_atual:
                    strengths = linha.split(':')[1].strip().split(',')
                    esporte_atual['strengths'] = [s.strip() for s in strengths if s.strip()]
            elif 'Desenvolvimento:' in linha or 'desenvolvimento:' in linha:
                if esporte_atual:
                    dev = linha.split(':')[1].strip().split(',')
                    esporte_atual['development'] = [d.strip() for d in dev if d.strip()]
        
        # Adiciona o último esporte
        if esporte_atual:
            recomendacoes.append(esporte_atual)
        
        return recomendacoes[:3]  # Retorna apenas os 3 primeiros esportes
    except Exception as e:
        print(f"Erro ao processar resposta: {str(e)}")
        return get_default_recommendations()

def get_default_recommendations():
    """
    Retorna recomendações padrão em caso de erro
    """
    return [
        {
            "name": "Natação",
            "compatibility": 85,
            "strengths": ["Resistência cardiovascular", "Coordenação motora"],
            "development": ["Força explosiva", "Velocidade"]
        },
        {
            "name": "Atletismo",
            "compatibility": 80,
            "strengths": ["Velocidade", "Resistência"],
            "development": ["Coordenação fina", "Equilíbrio"]
        },
        {
            "name": "Basquete",
            "compatibility": 75,
            "strengths": ["Altura", "Coordenação"],
            "development": ["Resistência", "Agilidade"]
        }
    ]
