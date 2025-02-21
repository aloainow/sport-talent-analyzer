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
            return max(0, min(100, ((max_val - value) / (max_val - min_val)) * 100))
        return max(0, min(100, ((value - min_val) / (max_val - min_val)) * 100))
    except (TypeError, ValueError):
        return 0

# Dicionário de traduções de termos gerais
SPORTS_TRANSLATIONS = {
    # Esportes Principais
    "Athletics": "Atletismo",
    "Swimming": "Natação",
    "Gymnastics": "Ginástica",
    "Wrestling": "Luta Livre",
    "Boxing": "Boxe",
    "Weightlifting": "Levantamento de Peso",
    "Cycling": "Ciclismo",
    "Fencing": "Esgrima",
    "Shooting": "Tiro",
    "Diving": "Saltos Ornamentais",
    "Basketball": "Basquete",
    "Volleyball": "Vôlei",
    "Football": "Futebol",
    "Handball": "Handebol",
    "Water Polo": "Polo Aquático",
    "Baseball": "Beisebol",
    "Tennis": "Tênis",
    "Table Tennis": "Tênis de Mesa",
    "Badminton": "Badminton",
    "Hockey": "Hóquei",
    "Rugby": "Rúgbi",
    "Judo": "Judô",
    "Taekwondo": "Taekwondo",
    "Sailing": "Vela",
    "Rowing": "Remo",
    "Canoeing": "Canoagem",
    "Archery": "Tiro com Arco",
    
    # Categorias de Peso
    "Flyweight": "Peso Mosca",
    "Light-Flyweight": "Peso Mosca Ligeiro",
    "Bantamweight": "Peso Galo",
    "Featherweight": "Peso Pena",
    "Lightweight": "Peso Leve",
    "Welterweight": "Peso Meio-Médio",
    "Middleweight": "Peso Médio",
    "Light-Heavyweight": "Peso Meio-Pesado",
    "Heavyweight": "Peso Pesado",
    "Super-Heavyweight": "Peso Super-Pesado",
    
    # Tipos de Prova
    "Individual": "Individual",
    "Team": "Equipe",
    "Singles": "Individual",
    "Doubles": "Duplas",
    "Mixed": "Misto",
    "Freestyle": "Estilo Livre",
    "All-Around": "Individual Geral",
    
    # Distâncias e Medidas
    "metres": "metros",
    "Relay": "Revezamento",
    "Marathon": "Maratona",
    "Road Race": "Corrida de Estrada",
    
    # Direção e Gênero
    "Men's": "Masculino",
    "Women's": "Feminino"
}

# Dicionário de traduções de eventos completos
EVENT_TRANSLATIONS = {
    # Ginástica
    "Gymnastics Team All-Around, Free System": "Ginástica Equipe Geral, Sistema Livre",
    "Gymnastics Men's Floor Exercise": "Ginástica Solo",
    "Gymnastics Men's Horizontal Bar": "Ginástica Barra Fixa",
    "Gymnastics Men's Parallel Bars": "Ginástica Barras Paralelas",
    "Gymnastics Men's Rings": "Ginástica Argolas",
    "Gymnastics Women's Balance Beam": "Ginástica Trave",
    "Gymnastics Women's Uneven Bars": "Ginástica Barras Assimétricas",
    
    # Natação
    "Swimming Men's 100 metres Freestyle": "Natação 100 metros Nado Livre",
    "Swimming Men's 200 metres Freestyle": "Natação 200 metros Nado Livre",
    "Swimming Men's 400 metres Freestyle": "Natação 400 metros Nado Livre",
    "Swimming Men's 1,500 metres Freestyle": "Natação 1.500 metros Nado Livre",
    "Swimming Men's 100 metres Backstroke": "Natação 100 metros Costas",
    "Swimming Men's 200 metres Backstroke": "Natação 200 metros Costas",
    "Swimming Men's 100 metres Breaststroke": "Natação 100 metros Peito",
    "Swimming Men's 200 metres Breaststroke": "Natação 200 metros Peito",
    "Swimming Men's 100 metres Butterfly": "Natação 100 metros Borboleta",
    "Swimming Men's 200 metres Butterfly": "Natação 200 metros Borboleta",
    
    # Atletismo
    "Athletics Men's 100 metres": "Atletismo 100 metros",
    "Athletics Men's 200 metres": "Atletismo 200 metros",
    "Athletics Men's 400 metres": "Atletismo 400 metros",
    "Athletics Men's 800 metres": "Atletismo 800 metros",
    "Athletics Men's 1,500 metres": "Atletismo 1.500 metros",
    "Athletics Men's 5,000 metres": "Atletismo 5.000 metros",
    "Athletics Men's 10,000 metres": "Atletismo 10.000 metros",
    "Athletics Men's Marathon": "Atletismo Maratona",
    "Athletics Men's 110 metres Hurdles": "Atletismo 110 metros com Barreiras",
    "Athletics Men's 400 metres Hurdles": "Atletismo 400 metros com Barreiras",
    "Athletics Men's High Jump": "Atletismo Salto em Altura",
    "Athletics Men's Long Jump": "Atletismo Salto em Distância",
    "Athletics Men's Triple Jump": "Atletismo Salto Triplo",
    "Athletics Men's Pole Vault": "Atletismo Salto com Vara",
    "Athletics Men's Shot Put": "Atletismo Arremesso de Peso",
    "Athletics Men's Discus Throw": "Atletismo Lançamento de Disco",
    "Athletics Men's Hammer Throw": "Atletismo Lançamento de Martelo",
    "Athletics Men's Javelin Throw": "Atletismo Lançamento de Dardo",
    
    # Lutas
    "Boxing Men's Flyweight": "Boxe Peso Mosca",
    "Boxing Men's Bantamweight": "Boxe Peso Galo",
    "Boxing Men's Featherweight": "Boxe Peso Pena",
    "Boxing Men's Lightweight": "Boxe Peso Leve",
    "Boxing Men's Welterweight": "Boxe Peso Meio-Médio",
    "Boxing Men's Middleweight": "Boxe Peso Médio",
    "Boxing Men's Light-Heavyweight": "Boxe Peso Meio-Pesado",
    "Boxing Men's Heavyweight": "Boxe Peso Pesado",
    
    # Competições de Arte
    "Art Competitions Mixed Sculpturing": "Competições de Arte Escultura Mista",
    "Art Competitions Mixed Painting": "Competições de Arte Pintura Mista",
    "Art Competitions Mixed Literature": "Competições de Arte Literatura Mista",
    "Art Competitions Mixed Architecture": "Competições de Arte Arquitetura Mista",
    
    # Outros Esportes
    "Basketball Men's Basketball": "Basquete",
    "Volleyball Men's Volleyball": "Vôlei",
    "Football Men's Football": "Futebol",
    "Handball Men's Handball": "Handebol",
    "Water Polo Men's Water Polo": "Polo Aquático",
    "Beach Volleyball Men's Beach Volleyball": "Vôlei de Praia",
    "Cycling Men's Road Race, Individual": "Ciclismo Corrida de Estrada Individual",
    "Table Tennis Men's Singles": "Tênis de Mesa Individual",
    "Tennis Men's Singles": "Tênis Individual",
    "Judo Men's Lightweight": "Judô Peso Leve",
    "Taekwondo Men's Flyweight": "Taekwondo Peso Mosca",
    "Fencing Men's Foil, Individual": "Esgrima Florete Individual",
    "Archery Men's Individual": "Tiro com Arco Individual"
}

def load_and_process_data() -> pd.DataFrame:
    """
    Carrega e processa os dados dos esportes olímpicos
    """
    try:
        # Dados base dos esportes olímpicos
        sports_data = {
            'Event': [
                "Athletics Men's 100 metres",
                "Athletics Men's 200 metres",
                "Athletics Men's 400 metres",
                "Athletics Men's 800 metres",
                "Athletics Men's 1,500 metres",
                "Athletics Men's 5,000 metres",
                "Athletics Men's 10,000 metres",
                "Athletics Men's Marathon",
                "Athletics Men's High Jump",
                "Athletics Men's Long Jump",
                "Athletics Men's Triple Jump",
                "Athletics Men's Pole Vault",
                "Athletics Men's Shot Put",
                "Athletics Men's Discus Throw",
                "Athletics Men's Hammer Throw",
                "Athletics Men's Javelin Throw",
                "Swimming Men's 100 metres Freestyle",
                "Swimming Men's 200 metres Freestyle",
                "Swimming Men's 400 metres Freestyle",
                "Swimming Men's 1,500 metres Freestyle",
                "Swimming Men's 100 metres Backstroke",
                "Swimming Men's 200 metres Backstroke",
                "Swimming Men's 100 metres Breaststroke",
                "Swimming Men's 200 metres Breaststroke",
                "Swimming Men's 100 metres Butterfly",
                "Swimming Men's 200 metres Butterfly",
                "Gymnastics Men's Floor Exercise",
                "Gymnastics Men's Horizontal Bar",
                "Gymnastics Men's Parallel Bars",
                "Gymnastics Men's Rings",
                "Basketball Men's Basketball",
                "Volleyball Men's Volleyball",
                "Football Men's Football",
                "Boxing Men's Flyweight",
                "Boxing Men's Bantamweight",
                "Boxing Men's Featherweight",
                "Boxing Men's Lightweight",
                "Boxing Men's Welterweight",
                "Boxing Men's Middleweight",
                "Boxing Men's Light-Heavyweight",
                "Boxing Men's Heavyweight",
                "Athletics Women's 100 metres",
                "Athletics Women's 200 metres",
                "Athletics Women's 400 metres",
                "Athletics Women's 800 metres",
                "Athletics Women's 1,500 metres",
                "Athletics Women's 5,000 metres",
                "Athletics Women's 10,000 metres",
                "Athletics Women's Marathon",
                "Athletics Women's High Jump",
                "Athletics Women's Long Jump",
                "Athletics Women's Triple Jump",
                "Athletics Women's Pole Vault",
                "Athletics Women's Shot Put",
                "Athletics Women's Discus Throw",
                "Athletics Women's Hammer Throw",
                "Athletics Women's Javelin Throw",
                "Swimming Women's 100 metres Freestyle",
                "Swimming Women's 200 metres Freestyle",
                "Swimming Women's 400 metres Freestyle",
                "Swimming Women's 800 metres Freestyle",
                "Swimming Women's 100 metres Backstroke",
                "Swimming Women's 200 metres Backstroke",
                "Swimming Women's 100 metres Breaststroke",
                "Swimming Women's 200 metres Breaststroke",
                "Swimming Women's 100 metres Butterfly",
                "Swimming Women's 200 metres Butterfly",
                "Gymnastics Women's Balance Beam",
                "Gymnastics Women's Uneven Bars",
                "Gymnastics Women's Floor Exercise",
                "Basketball Women's Basketball",
                "Volleyball Women's Volleyball",
                "Football Women's Football"
            ]
        }
        
        # Converter para DataFrame
        df = pd.DataFrame(sports_data)
        
        # Adicionar colunas extras se necessário
        df['Sport'] = df['Event'].apply(lambda x: x.split()[0])
        df['Gender'] = df['Event'].apply(lambda x: 'Women' if "Women's" in x else 'Men')
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados dos esportes: {str(e)}")
        return None

def translate_sport_name(sport_name: str, user_gender: str) -> str:
    """
    Traduz o nome completo do evento esportivo de inglês para português
    """
    try:
        # Primeiro, tenta encontrar uma tradução direta
        base_event = sport_name.replace("Women's", "Men's")  # Normaliza para versão masculina
        if base_event in EVENT_TRANSLATIONS:
            translated_name = EVENT_TRANSLATIONS[base_event]
        else:
            # Se não encontrar, traduz parte por parte
            translated_name = sport_name
            for en, pt in SPORTS_TRANSLATIONS.items():
                translated_name = translated_name.replace(en, pt)
        
        # Remove menções de gênero em inglês
        translated_name = translated_name.replace("Men's", "").replace("Women's", "").strip()
        
        # Adiciona o gênero em português no final
        if "Mixed" not in sport_name and "Mista" not in translated_name:
            if "Women's" in sport_name or user_gender == "Feminino":
                translated_name += " Feminino"
            elif "Men's" in sport_name or user_gender == "Masculino":
                translated_name += " Masculino"
        
        # Limpa e formata o resultado final
        translated_name = " ".join(translated_name.split())
        return translated_name

    except Exception as e:
        st.warning(f"Erro na tradução do evento: {str(e)}")
        return sport_name  # Retorna o nome original em caso de erro

def calculate_physical_compatibility(user_data: Dict, sport_name: str, user_age: int = 18) -> float:
    """
    Calcula compatibilidade física baseada nos testes, ajustada pela idade
    """
    try:
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
            scores.append(velocity_score * 1.5)
        
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
        
        # Calcular média dos scores disponíveis
        if not scores:
            return 50
            
        base_score = np.mean(scores)
        
        # Ajuste baseado na idade
        age_factor = min(1.0, max(0.6, (user_age - 10) / 8))
        return base_score * age_factor
            
    except Exception as e:
        st.error(f"Erro no cálculo de compatibilidade física: {str(e)}")
        return 50

def calculate_biotype_compatibility(user_data: Dict, sport: pd.Series) -> float:
    """
    Calcula a compatibilidade do biotipo do usuário com o esporte
    """
    try:
        if not user_data.get('biotipo'):
            return 50  # Valor padrão se não houver dados de biotipo
            
        biotype_data = user_data['biotipo']
        sport_name = sport['Event'].lower()
        scores = []
        
        # Altura (150-220 cm)
        if 'altura' in biotype_data:
            height = biotype_data['altura']
            
            # Esportes que valorizam altura
            if any(s in sport_name for s in ['basketball', 'volleyball']):
                height_score = normalize_score(height, 170, 210)
                scores.append(height_score * 1.5)  # Peso maior para altura
            
            # Esportes que valorizam altura média/baixa
            elif any(s in sport_name for s in ['gymnastics', 'wrestling']):
                height_score = normalize_score(height, 150, 180)
                scores.append(height_score)
        
        # Peso (40-120 kg)
        if 'peso' in biotype_data:
            weight = biotype_data['peso']
            
            # Categorias de peso para esportes de combate
            if any(s in sport_name for s in ['boxing', 'wrestling', 'judo']):
                # Simplificação das categorias de peso
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
    strengths = []
    sport_name = sport_name.lower()
    
    try:
        # Avaliação de biotipo
        if user_data.get('biotipo'):
            if user_data['biotipo'].get('altura', 0) >= 180 and any(s in sport_name for s in ['basketball', 'volleyball']):
                strengths.append("Altura favorável")
            
            if user_data['biotipo'].get('envergadura', 0) >= 190 and any(s in sport_name for s in ['swimming', 'boxing']):
                strengths.append("Boa envergadura")
        
        # Avaliação física
        if user_data.get('dados_fisicos'):
            if user_data['dados_fisicos'].get('velocidade', 0) <= 3.0 and 'athletics' in sport_name:
                strengths.append("Velocidade")
                
            if user_data['dados_fisicos'].get('forca_superior', 0) >= 40:
                strengths.append("Força superior")
                
            if user_data['dados_fisicos'].get('forca_inferior', 0) >= 50:
                strengths.append("Força inferior")
        
        # Avaliação técnica
        if user_data.get('habilidades_tecnicas'):
            if user_data['habilidades_tecnicas'].get('coordenacao', 0) >= 40:
                strengths.append("Coordenação")
                
            if user_data['habilidades_tecnicas'].get('precisao', 0) >= 8:
                strengths.append("Precisão")
                
            if user_data['habilidades_tecnicas'].get('equilibrio', 0) >= 50:
                strengths.append("Equilíbrio")
        
        # Limitar a 3 pontos fortes principais
        return strengths[:3] if strengths else ["Avaliação pendente"]
        
    except Exception as e:
        st.warning(f"Erro ao identificar pontos fortes: {str(e)}")
        return ["Avaliação pendente"]

def get_development_areas(sport_name: str, user_data: Dict) -> List[str]:
    """
    Identifica áreas de desenvolvimento para um determinado esporte
    """
    areas = []
    sport_name = sport_name.lower()
    
    try:
        # Avaliação física
        if user_data.get('dados_fisicos'):
            if user_data['dados_fisicos'].get('velocidade', 6) > 4.0 and 'athletics' in sport_name:
                areas.append("Velocidade")
                
            if user_data['dados_fisicos'].get('forca_superior', 0) < 30:
                areas.append("Força superior")
                
            if user_data['dados_fisicos'].get('forca_inferior', 0) < 40:
                areas.append("Força inferior")
        
        # Avaliação técnica
        if user_data.get('habilidades_tecnicas'):
            if user_data['habilidades_tecnicas'].get('coordenacao', 0) < 30:
                areas.append("Coordenação")
                
            if user_data['habilidades_tecnicas'].get('precisao', 0) < 6:
                areas.append("Precisão")
                
            if user_data['habilidades_tecnicas'].get('equilibrio', 0) < 40:
                areas.append("Equilíbrio")
            
            if user_data['habilidades_tecnicas'].get('agilidade', 0) > 10:
                areas.append("Agilidade")
        
        # Limitar a 3 áreas principais de desenvolvimento
        return areas[:3] if areas else ["Avaliação pendente"]
        
    except Exception as e:
        st.warning(f"Erro ao identificar áreas de desenvolvimento: {str(e)}")
        return ["Avaliação pendente"]

import numpy as np
import streamlit as st
from typing import Dict, Any, List

import numpy as np
import streamlit as st
from typing import Dict, Any, List

def normalize_score(value, min_val, max_val, inverse=False):
    """Normaliza um valor para escala 0-100"""
    try:
        if value is None or value == "":
            return 0
        value = float(value)
        if inverse:
            return max(0, min(100, ((max_val - value) / (max_val - min_val)) * 100))
        return max(0, min(100, ((value - min_val) / (max_val - min_val)) * 100))
    except (TypeError, ValueError):
        return 0

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

        user_gender = user_data.get('genero', '').lower()
        user_age = user_data.get('idade', 18)

        # Filtragem correta de esportes por gênero
        if user_gender == "feminino":
            sports_data = sports_data[
                sports_data['Event'].str.contains("Women's|Mixed", case=False, na=False)
            ]
        elif user_gender == "masculino":
            sports_data = sports_data[
                sports_data['Event'].str.contains("Men's|Mixed", case=False, na=False)
            ]

        if sports_data.empty:
            st.warning("Nenhum esporte encontrado para o gênero selecionado.")
            return get_recommendations_without_api(user_gender)

        recommendations = []
        for _, sport in sports_data.iterrows():
            try:
                sport_name = sport['Event']
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

                # Calcular pontuação final ajustada pela idade
                base_score = (
                    (biotype_score if biotype_score else np.random.randint(30, 70)) * 0.30 +
                    (physical_score if physical_score else np.random.randint(30, 70)) * 0.25 +
                    (tech_score if tech_score else np.random.randint(30, 70)) * 0.25 +
                    (tactic_score if tactic_score else np.random.randint(30, 70)) * 0.20
                )

                age_factor = min(1.0, max(0.6, (user_age - 10) / 8))
                final_score = min(90, max(20, base_score * age_factor))  # Garante que fique entre 20 e 90

                translated_name = translate_sport_name(sport_name, user_gender)

                recommendations.append({
                    "name": translated_name,
                    "compatibility": round(final_score) if not np.isnan(final_score) else 0,
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
