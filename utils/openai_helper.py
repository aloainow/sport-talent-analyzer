import pandas as pd
import json
import numpy as np
from typing import Dict, List, Any
import os
import streamlit as st

def normalize_score(value, min_val, max_val, inverse=False):
    """Normaliza um valor para escala 0-100"""
    try:
        if value is None:
            return 0
        value = float(value)
        if inverse:
            if value <= min_val:
                return 100
            elif value >= max_val:
                return 0
            return ((max_val - value) / (max_val - min_val)) * 100
        else:
            if value >= max_val:
                return 100
            elif value <= min_val:
                return 0
            return ((value - min_val) / (max_val - min_val)) * 100
    except (TypeError, ValueError):
        return 0

def load_and_process_data():
    """
    Carrega e processa os dados olímpicos e perfis de esportes
    """
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(current_dir, 'data', 'perfil_eventos_olimpicos_verao.csv')
        olympic_data = pd.read_csv(csv_path)
        olympic_data['base_sport'] = olympic_data['Event'].apply(lambda x: x.split("'")[0].strip())
        return olympic_data

    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

def calculate_biotype_compatibility(user_data: Dict, sport_data: pd.Series) -> float:
    """
    Calcula compatibilidade biométrica com dados olímpicos
    """
    scores = []
    
    # Altura
    if 'altura' in user_data:
        height = user_data['altura']
        height_score = normalize_score(height, sport_data['altura_min'], sport_data['altura_max'])
        if sport_data['altura_min'] <= height <= sport_data['altura_max']:
            height_score += 20
        scores.append(height_score)
    
    # Peso
    if 'peso' in user_data:
        weight = user_data['peso']
        weight_score = normalize_score(weight, sport_data['peso_min'], sport_data['peso_max'])
        if sport_data['peso_min'] <= weight <= sport_data['peso_max']:
            weight_score += 20
        scores.append(weight_score)
    
    return np.mean(scores) if scores else 50

def calculate_physical_compatibility(user_data: Dict, sport_name: str) -> float:
    """
    Calcula compatibilidade física baseada nos testes
    """
    if not user_data.get('dados_fisicos'):
        return 50
        
    scores = []
    
    # Velocidade (esportes que valorizam velocidade)
    velocity_sports = ['Athletics', 'Swimming', 'Cycling', 'Sprint']
    if any(sport in sport_name for sport in velocity_sports):
        velocity_score = normalize_score(
            user_data['dados_fisicos'].get('velocidade', 5),
            2.5, 5.0, inverse=True
        )
        scores.append(velocity_score * 1.5)  # Peso maior para esportes de velocidade
    
    # Força (esportes que valorizam força)
    strength_sports = ['Weightlifting', 'Wrestling', 'Judo', 'Boxing']
    if any(sport in sport_name for sport in strength_sports):
        strength_upper = normalize_score(
            user_data['dados_fisicos'].get('forca_superior', 0),
            0, 50
        )
        strength_lower = normalize_score(
            user_data['dados_fisicos'].get('forca_inferior', 0),
            0, 60
        )
        scores.extend([strength_upper * 1.5, strength_lower * 1.5])
    
    return np.mean(scores) if scores else 50

# Dicionário de traduções de esportes
SPORTS_TRANSLATIONS = {
    # Atletismo
    "Athletics": "Atletismo",
    "metres": "metros",
    "Women's": "Feminino",
    "Men's": "Masculino",
    
    # Natação
    "Swimming": "Natação",
    "Freestyle": "Nado Livre",
    "Butterfly": "Borboleta",
    "Backstroke": "Costas",
    "Breaststroke": "Peito",
    "Individual Medley": "Medley",
    
    # Esportes coletivos
    "Basketball": "Basquete",
    "Volleyball": "Vôlei",
    "Football": "Futebol",
    "Handball": "Handebol",
    
    # Lutas
    "Wrestling": "Luta Livre",
    "Boxing": "Boxe",
    "Judo": "Judô",
    "Taekwondo": "Taekwondo",
    
    # Ginástica
    "Gymnastics": "Ginástica",
    "Artistic": "Artística",
    "Rhythmic": "Rítmica",
    
    # Outros esportes
    "Cycling": "Ciclismo",
    "Tennis": "Tênis",
    "Table Tennis": "Tênis de Mesa",
    "Weightlifting": "Levantamento de Peso",
    "Rowing": "Remo",
    "Sailing": "Vela",
    "Shooting": "Tiro",
    "Archery": "Tiro com Arco",
    "Fencing": "Esgrima",
    "Diving": "Saltos Ornamentais",
}

def translate_sport_name(sport_name: str) -> str:
    """
    Traduz o nome do esporte de inglês para português
    """
    translated_name = sport_name
    
    # Substituir cada termo em inglês pelo seu equivalente em português
    for en, pt in SPORTS_TRANSLATIONS.items():
        translated_name = translated_name.replace(en, pt)
    
    # Ajustar a formatação para ficar mais natural em português
    parts = translated_name.split()
    
    # Se contém indicação de gênero, move para o final
    if "Masculino" in parts or "Feminino" in parts:
        parts = [p for p in parts if p not in ["Masculino", "Feminino"]] + \
               [p for p in parts if p in ["Masculino", "Feminino"]]
    
    # Reconstrói o nome do esporte
    translated_name = " ".join(parts)
    
    # Remove espaços duplos que possam ter sido criados
    translated_name = " ".join(translated_name.split())
    
    return translated_name

def get_sport_strengths(sport_name: str, user_data: Dict) -> List[str]:
    """
    Determina pontos fortes para o esporte baseado nos dados do usuário
    """
    strengths = []
    
    # Análise do biótipo (prioridade para altura excepcional)
    altura = user_data.get('altura', 0)
    envergadura = user_data.get('envergadura', 0)
    
    # Altura acima de 200cm é uma vantagem significativa
    if altura >= 200:
        strengths.insert(0, "Altura Excepcional")  # Insere no início da lista como principal ponto forte
    elif altura >= 190:
        strengths.append("Altura Acima da Média")
        
    # Envergadura proporcional ou maior que altura é uma vantagem
    if envergadura >= altura or envergadura >= 190:
        strengths.append("Envergadura Favorável")
    
    # Análise física
    if user_data.get('dados_fisicos'):
        dados_fisicos = user_data['dados_fisicos']
        velocidade = dados_fisicos.get('velocidade')
        forca_superior = dados_fisicos.get('forca_superior')
        forca_inferior = dados_fisicos.get('forca_inferior')
        
        if velocidade is not None and velocidade <= 3.5:
            strengths.append("Velocidade")
        if forca_superior is not None and forca_superior >= 20:
            strengths.append("Força Superior")
        if forca_inferior is not None and forca_inferior >= 35:
            strengths.append("Força Inferior")
    
    # Análise técnica
    if user_data.get('habilidades_tecnicas'):
        hab_tecnicas = user_data['habilidades_tecnicas']
        coordenacao = hab_tecnicas.get('coordenacao')
        precisao = hab_tecnicas.get('precisao')
        equilibrio = hab_tecnicas.get('equilibrio')
        agilidade = hab_tecnicas.get('agilidade')
        
        if coordenacao is not None and coordenacao >= 25:
            strengths.append("Coordenação")
        if precisao is not None and precisao >= 7:
            strengths.append("Precisão")
        if equilibrio is not None and equilibrio >= 25:
            strengths.append("Equilíbrio")
        if agilidade is not None and agilidade <= 12:
            strengths.append("Agilidade")
    
    # Análise tática
    if user_data.get('aspectos_taticos'):
        taticos = user_data['aspectos_taticos']
        decisao = taticos.get('tomada_decisao')
        visao = taticos.get('visao_jogo')
        posicionamento = taticos.get('posicionamento')
        
        if decisao is not None and decisao >= 7:
            strengths.append("Tomada de Decisão")
        if visao is not None and visao >= 6:
            strengths.append("Visão de Jogo")
        if posicionamento is not None and posicionamento >= 8:
            strengths.append("Posicionamento")
    
    return strengths[:3]  # Retorna os 3 principais pontos fortes

def get_development_areas(sport_name: str, user_data: Dict) -> List[str]:
    """
    Determina áreas para desenvolvimento baseado nos dados do usuário
    """
    areas = []
    
    # Análise física
    if user_data.get('dados_fisicos'):
        dados_fisicos = user_data['dados_fisicos']
        velocidade = dados_fisicos.get('velocidade')
        forca_superior = dados_fisicos.get('forca_superior')
        forca_inferior = dados_fisicos.get('forca_inferior')
        
        if velocidade is not None and velocidade > 3.5:
            areas.append("Velocidade")
        if forca_superior is not None and forca_superior < 20:
            areas.append("Força Superior")
        if forca_inferior is not None and forca_inferior < 35:
            areas.append("Força Inferior")
    
    # Análise técnica
    if user_data.get('habilidades_tecnicas'):
        hab_tecnicas = user_data['habilidades_tecnicas']
        coordenacao = hab_tecnicas.get('coordenacao')
        precisao = hab_tecnicas.get('precisao')
        equilibrio = hab_tecnicas.get('equilibrio')
        agilidade = hab_tecnicas.get('agilidade')
        
        if coordenacao is not None and coordenacao < 25:
            areas.append("Coordenação")
        if precisao is not None and precisao < 7:
            areas.append("Precisão")
        if equilibrio is not None and equilibrio < 25:
            areas.append("Equilíbrio")
        if agilidade is not None and agilidade > 12:
            areas.append("Agilidade")
            
    # Análise tática
    if user_data.get('aspectos_taticos'):
        taticos = user_data['aspectos_taticos']
        decisao = taticos.get('tomada_decisao')
        visao = taticos.get('visao_jogo')
        posicionamento = taticos.get('posicionamento')
        
        if decisao is not None and decisao < 7:
            areas.append("Tomada de Decisão")
        if visao is not None and visao < 6:
            areas.append("Visão de Jogo")
        if posicionamento is not None and posicionamento < 8:
            areas.append("Posicionamento")

    # Verificar aspectos psicológicos
    if user_data.get('fatores_psicologicos'):
        psico = user_data['fatores_psicologicos']
        if psico.get('resiliencia', {}).get('erros', 0) < 5:
            areas.append("Resiliência a Erros")
        if psico.get('trabalho_equipe', {}).get('opinioes', 0) < 5:
            areas.append("Trabalho em Equipe")
    
    return areas[:3]  # Retorna as 3 principais áreas para desenvolvimento

def get_sport_recommendations(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Gera recomendações de esportes baseadas nos dados do usuário e estatísticas olímpicas
    """
    try:
        # Carregar dados
        sports_data = load_and_process_data()
        if sports_data is None:
            st.warning("Falha ao carregar dados. Exibindo sugestões padrão.")
            return get_recommendations_without_api(user_data.get('genero', 'Masculino'))

        # Obter o gênero do usuário
        user_gender = user_data.get('genero', '')

        # Filtrar eventos por gênero
        if user_gender == "Masculino":
            sports_data = sports_data[~sports_data['Event'].str.contains("Women", case=False)]
        elif user_gender == "Feminino":
            sports_data = sports_data[sports_data['Event'].str.contains("Women", case=False)]

        recommendations = []

        # Avaliar cada esporte
        for _, sport in sports_data.iterrows():
            sport_name = sport['Event']
            
            # Calcular compatibilidades
            biotype_score = calculate_biotype_compatibility(user_data, sport)
            physical_score = calculate_physical_compatibility(user_data, sport_name)

            # Calcular técnica e tática baseado nos testes
            technical_score = 50  # Score base
            if user_data.get('habilidades_tecnicas'):
                tech_scores = [
                    normalize_score(user_data['habilidades_tecnicas'].get('coordenacao', 0), 0, 50),
                    normalize_score(user_data['habilidades_tecnicas'].get('precisao', 0), 0, 10),
                    normalize_score(user_data['habilidades_tecnicas'].get('equilibrio', 0), 0, 60)
                ]
               
                technical_score = np.mean(tech_scores)

            tactical_score = 50  # Score base
            if user_data.get('aspectos_taticos'):
                tactic_scores = [
                    normalize_score(user_data['aspectos_taticos'].get('tomada_decisao', 0), 0, 10),
                    normalize_score(user_data['aspectos_taticos'].get('visao_jogo', 0), 0, 10),
                    normalize_score(user_data['aspectos_taticos'].get('posicionamento', 0), 0, 10)
                ]
                tactical_score = np.mean(tactic_scores)

            # Calcular score final
            final_score = np.nanmean([
                biotype_score * 0.3,
                physical_score * 0.3,
                technical_score * 0.2,
                tactical_score * 0.2
            ])

            # Traduzir o nome do esporte antes de adicionar à recomendação
            translated_name = translate_sport_name(sport_name)
            
            recommendations.append({
                "name": translated_name,
                "compatibility": round(final_score) if not np.isnan(final_score) else 0,
                "strengths": get_sport_strengths(sport_name, user_data),
                "development": get_development_areas(sport_name, user_data)
            })

        # Ordenar e retornar até 10 recomendações
        recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
        
        if not recommendations:
            st.warning("Nenhum esporte foi recomendado. Exibindo sugestões padrão.")
            return get_recommendations_without_api(user_data.get('genero', 'Masculino'))

        return recommendations[:10]

    except Exception as e:
        st.error(f"Erro ao gerar recomendações: {str(e)}")
        return get_recommendations_without_api(user_data.get('genero', 'Masculino'))

def get_recommendations_without_api(gender: str = "Masculino") -> List[Dict[str, Any]]:
    """
    Retorna recomendações padrão caso haja problema com os dados
    
    Args:
        gender (str): Gênero do usuário ("Masculino", "Feminino" ou outro)
        
    Returns:
        List[Dict[str, Any]]: Lista de recomendações padrão
    """
    if gender == "Masculino":
        return [
            {
                "name": "Basquete Masculino",
                "compatibility": 95,
                "strengths": ["Altura Excepcional", "Envergadura Favorável"],
                "development": ["Agilidade", "Coordenação"]
            },
            {
                "name": "Vôlei Masculino",
                "compatibility": 90,
                "strengths": ["Altura Excepcional", "Força Superior"],
                "development": ["Velocidade", "Resistência"]
            },
            {
                "name": "Atletismo Lançamento de Dardo Masculino",
                "compatibility": 85,
                "strengths": ["Força Superior", "Envergadura"],
                "development": ["Técnica específica", "Equilíbrio"]
            },
            {
                "name": "Handebol Masculino",
                "compatibility": 82,
                "strengths": ["Altura", "Força"],
                "development": ["Agilidade", "Resistência"]
            },
            {
                "name": "Saltos Ornamentais Masculino",
                "compatibility": 78,
                "strengths": ["Altura", "Força Explosiva"],
                "development": ["Flexibilidade", "Precisão"]
            }
        ]
    elif gender == "Feminino":
        return [
            {
                "name": "Basquete Feminino",
                "compatibility": 95,
                "strengths": ["Altura Excepcional", "Envergadura Favorável"],
                "development": ["Agilidade", "Coordenação"]
            },
            {
                "name": "Vôlei Feminino",
                "compatibility": 90,
                "strengths": ["Altura Excepcional", "Força Superior"],
                "development": ["Velocidade", "Resistência"]
            },
            {
                "name": "Atletismo Lançamento de Dardo Feminino",
                "compatibility": 85,
                "strengths": ["Força Superior", "Envergadura"],
                "development": ["Técnica específica", "Equilíbrio"]
            },
            {
                "name": "Handebol Feminino",
                "compatibility": 82,
                "strengths": ["Altura", "Força"],
                "development": ["Agilidade", "Resistência"]
            },
            {
                "name": "Ginástica Rítmica",
                "compatibility": 78,
                "strengths": ["Altura", "Flexibilidade"],
                "development": ["Força", "Equilíbrio"]
            }
        ]
    else:
        return [
            {
                "name": "Basquete",
                "compatibility": 95,
                "strengths": ["Altura Excepcional", "Envergadura Favorável"],
                "development": ["Agilidade", "Coordenação"]
            },
            {
                "name": "Vôlei",
                "compatibility": 90,
                "strengths": ["Altura Excepcional", "Força Superior"],
                "development": ["Velocidade", "Resistência"]
            },
            {
                "name": "Atletismo Lançamento de Dardo",
                "compatibility": 85,
                "strengths": ["Força Superior", "Envergadura"],
                "development": ["Técnica específica", "Equilíbrio"]
            },
            {
                "name": "Handebol",
                "compatibility": 82,
                "strengths": ["Altura", "Força"],
                "development": ["Agilidade", "Resistência"]
            },
            {
                "name": "Saltos Ornamentais",
                "compatibility": 78,
                "strengths": ["Altura", "Força Explosiva"],
                "development": ["Flexibilidade", "Precisão"]
            }
        ]
