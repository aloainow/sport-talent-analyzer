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
            return get_recommendations_without_api()

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

            # Calcular score final (tratando NaN)
            final_score = np.nanmean([
                biotype_score * 0.3,
                physical_score * 0.3,
                technical_score * 0.2,
                tactical_score * 0.2
            ])

            # Debug de compatibilidades
            st.write(f"{sport_name}: Biotipo {biotype_score:.1f}, Físico {physical_score:.1f}, Técnico {technical_score:.1f}, Tático {tactical_score:.1f}, Final {final_score:.1f}")

            # Adicionar independente do valor final, tratando NaN
            recommendations.append({
                "name": sport_name,
                "compatibility": round(final_score) if not np.isnan(final_score) else 0,
                "strengths": get_sport_strengths(sport_name, user_data),
                "development": get_development_areas(sport_name, user_data)
            })

        # Ordenar e retornar até 10 recomendações
        recommendations.sort(key=lambda x: x['compatibility'], reverse=True)

        # Se nenhuma recomendação tiver sido feita, retorna padrão
        if not recommendations:
            st.warning("Nenhum esporte foi recomendado. Exibindo sugestões padrão.")
            return get_recommendations_without_api()

        st.write(f"Esportes recomendados: {len(recommendations)}")
        return recommendations[:10]

    except Exception as e:
        st.error(f"Erro ao gerar recomendações: {str(e)}")
        return get_recommendations_without_api()



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
