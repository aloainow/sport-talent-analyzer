import pandas as pd
import json
import numpy as np
from typing import Dict, List, Any
import os

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

        # Carregar dados olímpicos
        csv_path = os.path.join(current_dir, 'data', 'perfil_eventos_olimpicos_verao.csv')
        olympic_data = pd.read_csv(csv_path)

        # Só pra manter se for útil depois
        olympic_data['base_sport'] = olympic_data['Event'].apply(lambda x: x.split("'")[0].strip())

        return olympic_data  # <-- Não faz mais agrupamento

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
    # Ex: "Swimming Men's 100 metres Freestyle" -> "Natação 100 metros Nado Livre Masculino"
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

def get_sport_recommendations(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Gera recomendações de esportes baseadas nos dados do usuário e estatísticas olímpicas
    """
    import streamlit as st

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
            
            # Calcular scores e compatibilidade
            biotype_score = calculate_biotype_compatibility(user_data, sport)
            physical_score = calculate_physical_compatibility(user_data, sport_name)
            
            # [... resto do código de cálculo de scores ...]

            # Traduzir o nome do esporte antes de adicionar à recomendação
            translated_name = translate_sport_name(sport_name)
            
            recommendations.append({
                "name": translated_name,  # Nome traduzido
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

def get_recommendations_without_api(gender="Masculino"):
    """Retorna recomendações padrão caso haja problema com os dados"""
    if gender == "Masculino":
        return [
            {
                "name": "Atletismo 100 metros Masculino",
                "compatibility": 85,
                "strengths": ["Condicionamento físico geral", "Resistência"],
                "development": ["Técnica específica"]
            },
            {
                "name": "Natação 100 metros Nado Livre Masculino",
                "compatibility": 80,
                "strengths": ["Resistência cardiovascular", "Coordenação"],
                "development": ["Força muscular"]
            },
            {
                "name": "Basquete Masculino",
                "compatibility": 75,
                "strengths": ["Altura", "Coordenação"],
                "development": ["Resistência"]
            }
        ]
    elif gender == "Feminino":
        return [
            {
                "name": "Atletismo 100 metros Feminino",
                "compatibility": 85,
                "strengths": ["Condicionamento físico geral", "Resistência"],
                "development": ["Técnica específica"]
            },
            {
                "name": "Natação 100 metros Nado Livre Feminino",
                "compatibility": 80,
                "strengths": ["Resistência cardiovascular", "Coordenação"],
                "development": ["Força muscular"]
            },
            {
                "name": "Basquete Feminino",
                "compatibility": 75,
                "strengths": ["Altura", "Coordenação"],
                "development": ["Resistência"]
            }
        ]
    else:
        return [
            {
                "name": "Atletismo",
                "compatibility": 85,
                "strengths": ["Condicionamento físico geral", "Resistência"],
                "development": ["Técnica específica"]
            },
            {
                "name": "Natação",
                "compatibility": 80,
                "strengths": ["Resistência cardiovascular", "Coordenação"],
                "development": ["Força muscular"]
            },
            {
                "name": "Basquete",
                "compatibility": 75,
                "strengths": ["Altura", "Coordenação"],
                "development": ["Resistência"]
            }
        ]
def get_recommendations_without_api(gender="Masculino"):
    """Retorna recomendações padrão caso haja problema com os dados"""
    if gender == "Masculino":
        return [
            {
                "name": "Athletics Men's 100 metres",
                "compatibility": 85,
                "strengths": ["Condicionamento físico geral", "Resistência"],
                "development": ["Técnica específica"]
            },
            {
                "name": "Swimming Men's 100 metres Freestyle",
                "compatibility": 80,
                "strengths": ["Resistência cardiovascular", "Coordenação"],
                "development": ["Força muscular"]
            },
            {
                "name": "Basketball Men's Basketball",
                "compatibility": 75,
                "strengths": ["Altura", "Coordenação"],
                "development": ["Resistência"]
            }
        ]
    elif gender == "Feminino":
        return [
            {
                "name": "Athletics Women's 100 metres",
                "compatibility": 85,
                "strengths": ["Condicionamento físico geral", "Resistência"],
                "development": ["Técnica específica"]
            },
            {
                "name": "Swimming Women's 100 metres Freestyle",
                "compatibility": 80,
                "strengths": ["Resistência cardiovascular", "Coordenação"],
                "development": ["Força muscular"]
            },
            {
                "name": "Basketball Women's Basketball",
                "compatibility": 75,
                "strengths": ["Altura", "Coordenação"],
                "development": ["Resistência"]
            }
        ]
    else:
        # Para "Prefiro não informar", retorna mix de eventos
        return [
            {
                "name": "Athletics",
                "compatibility": 85,
                "strengths": ["Condicionamento físico geral", "Resistência"],
                "development": ["Técnica específica"]
            },
            {
                "name": "Swimming",
                "compatibility": 80,
                "strengths": ["Resistência cardiovascular", "Coordenação"],
                "development": ["Força muscular"]
            },
            {
                "name": "Basketball",
                "compatibility": 75,
                "strengths": ["Altura", "Coordenação"],
                "development": ["Resistência"]
            }
        ]


def get_sport_strengths(sport_name: str, user_data: Dict) -> List[str]:
    """
    Determina pontos fortes para o esporte baseado nos dados do usuário
    """
    strengths = []
    
    # Análise física
    if user_data.get('dados_fisicos'):
        if user_data['dados_fisicos'].get('velocidade', 5) < 3.5:
            strengths.append("Velocidade")
        if user_data['dados_fisicos'].get('forca_superior', 0) > 25:
            strengths.append("Força Superior")
        if user_data['dados_fisicos'].get('forca_inferior', 0) > 40:
            strengths.append("Força Inferior")
    
    # Análise técnica
    if user_data.get('habilidades_tecnicas'):
        if user_data['habilidades_tecnicas'].get('coordenacao', 0) > 30:
            strengths.append("Coordenação")
        if user_data['habilidades_tecnicas'].get('precisao', 0) > 7:
            strengths.append("Precisão")
        if user_data['habilidades_tecnicas'].get('equilibrio', 0) > 40:
            strengths.append("Equilíbrio")
    
    return strengths[:2]  # Retorna os 2 principais pontos fortes

def get_development_areas(sport_name: str, user_data: Dict) -> List[str]:
    """
    Determina áreas para desenvolvimento baseado nos dados do usuário
    """
    areas = []
    
    # Análise física
    if user_data.get('dados_fisicos'):
        if user_data['dados_fisicos'].get('velocidade', 5) > 4:
            areas.append("Velocidade")
        if user_data['dados_fisicos'].get('forca_superior', 0) < 15:
            areas.append("Força Superior")
        if user_data['dados_fisicos'].get('forca_inferior', 0) < 30:
            areas.append("Força Inferior")
    
    # Análise técnica
    if user_data.get('habilidades_tecnicas'):
        if user_data['habilidades_tecnicas'].get('coordenacao', 0) < 20:
            areas.append("Coordenação")
        if user_data['habilidades_tecnicas'].get('precisao', 0) < 5:
            areas.append("Precisão")
        if user_data['habilidades_tecnicas'].get('equilibrio', 0) < 20:
            areas.append("Equilíbrio")
    
    return areas[:2]  # Retorna as 2 principais áreas para desenvolvimento

def get_recommendations_without_api():
    """Retorna recomendações padrão caso haja problema com os dados"""
    return [
        {
            "name": "Athletics",
            "compatibility": 85,
            "strengths": ["Condicionamento físico geral", "Resistência"],
            "development": ["Técnica específica"]
        },
        {
            "name": "Swimming",
            "compatibility": 80,
            "strengths": ["Resistência cardiovascular", "Coordenação"],
            "development": ["Força muscular"]
        },
        {
            "name": "Cycling",
            "compatibility": 75,
            "strengths": ["Resistência", "Força nas pernas"],
            "development": ["Equilíbrio"]
        }
    ]

