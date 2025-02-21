import pandas as pd
import json
import numpy as np
from typing import Dict, List, Any
import os
import streamlit as st

def normalize_score(value, min_val, max_val, inverse=False):
    """Normaliza um valor para escala 0-100"""
    try:
        if value is None or value == "":
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

# ... [Keep your existing dictionaries like SPORTS_TRANSLATIONS and EVENT_TRANSLATIONS]

def load_and_process_data() -> pd.DataFrame:
    """
    Carrega e processa os dados dos esportes olímpicos
    """
    try:
        # Read the Olympic events CSV file
        df = pd.read_csv('perfil_eventos_olimpicos_verao.csv', encoding='utf-8')
        
        # Create a full Event column if it doesn't exist
        if 'Event' not in df.columns:
            df['Event'] = df['Sport'] + " " + df['Gender'] + "'s " + df['Distance/Category']
        
        # Ensure consistent naming convention
        df['Sport'] = df['Sport'].str.title()
        df['Gender'] = df['Gender'].apply(lambda x: "Women's" if x.lower() == 'female' else "Men's")
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados dos esportes: {str(e)}")
        return None
        
def translate_sport_name(sport_name: str, user_gender: str) -> str:
    """
    Traduz o nome completo do evento esportivo de inglês para português
    """
    # Your existing implementation

def calculate_physical_compatibility(user_data: Dict, sport_name: str, user_age: int = 18) -> float:
    """
    Calcula compatibilidade física baseada nos testes, ajustada pela idade
    """
    # Your existing implementation

def calculate_biotype_compatibility(user_data: Dict, sport: pd.Series) -> float:
    """
    Calcula a compatibilidade do biotipo do usuário com o esporte
    """
    try:
        if not user_data or 'biotipo' not in user_data:
            return 50  # Valor padrão se não houver dados de biotipo
            
        biotype_data = user_data.get('biotipo', {})
        sport_name = sport['Event'].lower()
        scores = []
        
        # Altura (150-220 cm)
        if 'altura' in biotype_data:
            height = biotype_data['altura']
            
            # Esportes que valorizam altura
            if any(s in sport_name for s in ['basketball', 'volleyball']):
                height_score = normalize_score(height, 170, 210)
                scores.append(height_score * 1.5)  # Peso maior para altura
        
        # Peso (40-120 kg)
        if 'peso' in biotype_data:
            weight = biotype_data['peso']
            
            # Categorias de peso para esportes de combate
            if any(s in sport_name for s in ['boxing', 'wrestling', 'judo']):
                if 'heavyweight' in sport_name:
                    weight_score = normalize_score(weight, 80, 120)
                elif 'middleweight' in sport_name:
                    weight_score = normalize_score(weight, 70, 85)
                elif 'lightweight' in sport_name:
                    weight_score = normalize_score(weight, 50, 70)
                else:
                    weight_score = normalize_score(weight, 40, 120)
                scores.append(weight_score * 1.3)
        
        # Envergadura (150-220 cm)
        if 'envergadura' in biotype_data:
            wingspan = biotype_data['envergadura']
            
            # Esportes que valorizam envergadura
            if any(s in sport_name for s in ['swimming', 'boxing', 'basketball']):
                wingspan_score = normalize_score(wingspan, 170, 220)
                scores.append(wingspan_score * 1.2)
        
        # Se não houver scores, retorna valor padrão
        if not scores:
            return 50
            
        # Retorna média dos scores
        return np.mean(scores)
        
    except Exception as e:
        st.warning(f"Erro no cálculo de compatibilidade de biotipo: {str(e)}")
        return 50

def get_sport_strengths(sport_name: str, user_data: Dict) -> List[str]:
    """
    Identifica os pontos fortes do usuário para um determinado esporte
    """
    # Your existing implementation

def get_development_areas(sport_name: str, user_data: Dict) -> List[str]:
    """
    Identifica áreas de desenvolvimento para um determinado esporte
    """
    # Your existing implementation

def get_sport_recommendations(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Gera recomendações de esportes baseadas nos dados do usuário
    """
    try:
        if not user_data or not all(user_data.get(key) for key in ['dados_fisicos', 'habilidades_tecnicas', 'aspectos_taticos', 'fatores_psicologicos']):
            st.error("Por favor, complete todos os testes antes de gerar recomendações.")
            return []

        sports_data = load_and_process_data()
        if sports_data is None:
            st.warning("Falha ao carregar dados. Exibindo sugestões padrão.")
            return get_recommendations_without_api(user_data.get('genero', 'Masculino'))

        user_gender = user_data.get('genero', '')
        user_age = user_data.get('idade', 18)

        # Filtrar esportes por gênero
        if user_gender == "Feminino":
            sports_data = sports_data[sports_data['Gender'] == "Women's"]
        elif user_gender == "Masculino":
            sports_data = sports_data[sports_data['Gender'] == "Men's"]

        if sports_data.empty:
            st.warning("Nenhum esporte encontrado para o gênero selecionado")
            return get_recommendations_without_api(user_gender)

        recommendations = []

        for _, sport in sports_data.iterrows():
            try:
                sport_name = sport['Event']
                
                # Calcular compatibilidade
                biotype_score = calculate_biotype_compatibility(user_data, sport)
                physical_score = calculate_physical_compatibility(user_data, sport_name, user_age)

                tech_score = np.mean([
                    normalize_score(user_data['habilidades_tecnicas'].get(metric, 0), 0, 50)
                    for metric in ['coordenacao', 'precisao', 'agilidade', 'equilibrio']
                    if metric in user_data['habilidades_tecnicas']
                ]) if user_data.get('habilidades_tecnicas') else 50

                tactic_score = np.mean([
                    normalize_score(user_data['aspectos_taticos'].get(metric, 0), 0, 10)
                    for metric in ['tomada_decisao', 'visao_jogo', 'posicionamento']
                    if metric in user_data['aspectos_taticos']
                ]) if user_data.get('aspectos_taticos') else 50

                base_score = (
                    biotype_score * 0.30 +
                    physical_score * 0.25 +
                    tech_score * 0.25 +
                    tactic_score * 0.20
                ) * 0.7

                # Ajustes adicionais
                if user_data.get('altura', 0) >= 180 and any(s in sport_name.lower() for s in ['basketball', 'volleyball']):
                    base_score *= 1.1

                age_factor = min(1.0, max(0.6, (user_age - 10) / 8))
                random_factor = np.random.uniform(0.9, 1.1)
                
                final_score = min(100, max(20, base_score * age_factor * random_factor))

                translated_name = translate_sport_name(sport_name, user_gender)

                recommendations.append({
                    "name": translated_name,
                    "compatibility": round(final_score),
                    "strengths": get_sport_strengths(sport_name, user_data),
                    "development": get_development_areas(sport_name, user_data)
                })
            except Exception as e:
                st.warning(f"Erro ao processar esporte {sport_name}: {str(e)}")
                continue

        recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
        return recommendations[:10]

    except Exception as e:
        st.error(f"Erro ao gerar recomendações: {str(e)}")
        return get_recommendations_without_api(user_data.get('genero', 'Masculino'))
        
def get_recommendations_without_api(gender: str = "Masculino") -> List[Dict[str, Any]]:
    """
    Retorna recomendações padrão caso haja problema com os dados
    """
    if gender == "Masculino":
        return [
            {
                "name": "Basquete Masculino",
                "compatibility": 75,
                "strengths": ["Altura", "Coordenação"],
                "development": ["Agilidade", "Resistência"]
            },
            {
                "name": "Vôlei Masculino",
                "compatibility": 70,
                "strengths": ["Altura", "Força Superior"],
                "development": ["Velocidade", "Resistência"]
            },
            {
                "name": "Atletismo Lançamento de Dardo Masculino",
                "compatibility": 65,
                "strengths": ["Força Superior", "Coordenação"],
                "development": ["Técnica específica", "Equilíbrio"]
            }
        ]
    elif gender == "Feminino":
        return [
            {
                "name": "Basquete Feminino",
                "compatibility": 75,
                "strengths": ["Altura", "Coordenação"],
                "development": ["Agilidade", "Resistência"]
            },
            {
                "name": "Vôlei Feminino",
                "compatibility": 70,
                "strengths": ["Altura", "Força Superior"],
                "development": ["Velocidade", "Resistência"]
            },
            {
                "name": "Ginástica Rítmica",
                "compatibility": 65,
                "strengths": ["Flexibilidade", "Coordenação"],
                "development": ["Força", "Equilíbrio"]
            }
        ]
    else:
        return [
            {
                "name": "Basquete",
                "compatibility": 75,
                "strengths": ["Altura", "Coordenação"],
                "development": ["Agilidade", "Resistência"]
            },
            {
                "name": "Vôlei",
                "compatibility": 70,
                "strengths": ["Altura", "Força Superior"],
                "development": ["Velocidade", "Resistência"]
            },
            {
                "name": "Atletismo",
                "compatibility": 65,
                "strengths": ["Força", "Coordenação"],
                "development": ["Técnica", "Resistência"]
            }
        ]
