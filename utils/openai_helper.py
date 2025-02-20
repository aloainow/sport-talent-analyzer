import pandas as pd
import numpy as np
from typing import Dict, List, Any

def calculate_compatibility_score(user_data: Dict[str, Any], event_data: pd.Series) -> float:
    """
    Calculate compatibility score between user data and event requirements
    """
    score = 0
    total_weight = 0
    
    # Physical attributes matching (height and weight)
    if 'altura' in user_data and 'peso' in user_data:
        # Height compatibility
        height_score = max(0, 100 - abs(user_data['altura'] - event_data['altura_media']) * 2)
        if event_data['altura_min'] <= user_data['altura'] <= event_data['altura_max']:
            height_score += 20
        score += height_score * 0.3
        
        # Weight compatibility
        weight_score = max(0, 100 - abs(user_data['peso'] - event_data['peso_media']) * 2)
        if event_data['peso_min'] <= user_data['peso'] <= event_data['peso_max']:
            weight_score += 20
        score += weight_score * 0.3
        
        total_weight += 0.6

    # Performance metrics
    if 'dados_fisicos' in user_data:
        physical_score = 0
        # Speed-based sports get bonus from velocity test
        if user_data['dados_fisicos'].get('velocidade'):
            speed_score = max(0, 100 - (user_data['dados_fisicos']['velocidade'] - 2.5) * 20)
            physical_score += speed_score
        
        # Strength-based sports get bonus from strength tests
        strength_score = (
            user_data['dados_fisicos'].get('forca_superior', 0) * 1.5 +
            user_data['dados_fisicos'].get('forca_inferior', 0) * 1.5
        ) / 2
        physical_score += strength_score
        
        score += (physical_score / 2) * 0.2
        total_weight += 0.2

    # Technical skills
    if 'habilidades_tecnicas' in user_data:
        tech_score = (
            user_data['habilidades_tecnicas'].get('coordenacao', 0) * 2 +
            user_data['habilidades_tecnicas'].get('precisao', 0) * 10 +
            max(0, 100 - user_data['habilidades_tecnicas'].get('agilidade', 0) * 6.67) +
            user_data['habilidades_tecnicas'].get('equilibrio', 0) * 1.67
        ) / 4
        
        score += tech_score * 0.1
        total_weight += 0.1

    # Tactical aspects
    if 'aspectos_taticos' in user_data:
        tactical_score = (
            user_data['aspectos_taticos'].get('tomada_decisao', 0) * 10 +
            user_data['aspectos_taticos'].get('visao_jogo', 0) * 10 +
            user_data['aspectos_taticos'].get('posicionamento', 0) * 10
        ) / 3
        
        score += tactical_score * 0.1
        total_weight += 0.1

    # Normalize final score
    if total_weight > 0:
        final_score = (score / total_weight)
        return min(max(final_score, 0), 100)
    return 0

def get_sport_strengths(event: str, user_data: Dict[str, Any]) -> List[str]:
    """
    Determine strengths for recommended sport based on user data
    """
    strengths = []
    
    if 'dados_fisicos' in user_data:
        if user_data['dados_fisicos'].get('velocidade', 5) < 3.5:
            strengths.append("Velocidade")
        if user_data['dados_fisicos'].get('forca_superior', 0) > 25:
            strengths.append("Força Superior")
        if user_data['dados_fisicos'].get('forca_inferior', 0) > 40:
            strengths.append("Força Inferior")
            
    if 'habilidades_tecnicas' in user_data:
        if user_data['habilidades_tecnicas'].get('coordenacao', 0) > 30:
            strengths.append("Coordenação")
        if user_data['habilidades_tecnicas'].get('precisao', 0) > 7:
            strengths.append("Precisão")
        if user_data['habilidades_tecnicas'].get('equilibrio', 0) > 40:
            strengths.append("Equilíbrio")
            
    return strengths[:2]  # Return top 2 strengths

def get_development_areas(event: str, user_data: Dict[str, Any]) -> List[str]:
    """
    Determine areas for development based on user data
    """
    development = []
    
    if 'dados_fisicos' in user_data:
        if user_data['dados_fisicos'].get('velocidade', 5) > 4:
            development.append("Velocidade")
        if user_data['dados_fisicos'].get('forca_superior', 0) < 15:
            development.append("Força Superior")
        if user_data['dados_fisicos'].get('forca_inferior', 0) < 30:
            development.append("Força Inferior")
            
    if 'habilidades_tecnicas' in user_data:
        if user_data['habilidades_tecnicas'].get('coordenacao', 0) < 20:
            development.append("Coordenação")
        if user_data['habilidades_tecnicas'].get('precisao', 0) < 5:
            development.append("Precisão")
        if user_data['habilidades_tecnicas'].get('equilibrio', 0) < 20:
            development.append("Equilíbrio")
            
    return development[:2]  # Return top 2 areas for development

def get_sport_recommendations(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate sport recommendations based on user data and Olympic sports database
    """
    try:
        # Read the Olympic sports database
        import os
        
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(current_dir, 'data', 'perfil_eventos_olimpicos_verao.csv')
        
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Calculate compatibility scores for each sport
        recommendations = []
        for _, event in df.iterrows():
            compatibility = calculate_compatibility_score(user_data, event)
            if compatibility >= 50:  # Only include sports with >50% compatibility
                recommendations.append({
                    "name": event['Event'],
                    "compatibility": round(compatibility),
                    "strengths": get_sport_strengths(event['Event'], user_data),
                    "development": get_development_areas(event['Event'], user_data)
                })
        
        # Sort by compatibility score and get top 5
        recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
        return recommendations[:5]
        
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return get_recommendations_without_api()  
