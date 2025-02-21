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

def get_sport_recommendations(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Gera recomendações de esportes baseadas nos dados do usuário
    """
    try:
        # Verificar dados do usuário
        if not user_data:
            st.error("Dados do usuário não fornecidos")
            return get_recommendations_without_api(user_data.get('genero', 'Masculino'))

        # Carregar dados
        sports_data = load_and_process_data()
        if sports_data is None:
            st.warning("Falha ao carregar dados. Exibindo sugestões padrão.")
            return get_recommendations_without_api(user_data.get('genero', 'Masculino'))

        # Obter dados básicos do usuário
        user_gender = user_data.get('genero', '')
        user_age = user_data.get('idade', 18)

        # Filtrar eventos por gênero
        try:
            if user_gender == "Feminino":
                sports_data = sports_data[
                    (sports_data['Event'].str.contains("Women", case=False)) |
                    (sports_data['Event'].str.contains("Mixed", case=False))
                ]
            elif user_gender == "Masculino":
                sports_data = sports_data[
                    (sports_data['Event'].str.contains("Men", case=False) & 
                     ~sports_data['Event'].str.contains("Women", case=False)) |
                    (sports_data['Event'].str.contains("Mixed", case=False))
                ]

            if len(sports_data) == 0:
                st.warning("Nenhum esporte encontrado para o gênero selecionado")
                return get_recommendations_without_api(user_gender)

        except Exception as e:
            st.error(f"Erro ao filtrar eventos por gênero: {str(e)}")
            return get_recommendations_without_api(user_gender)

        recommendations = []

        # Avaliar cada esporte
        for _, sport in sports_data.iterrows():
            try:
                sport_name = sport['Event']
                
                # Calcular scores individuais
                biotype_score = calculate_biotype_compatibility(user_data, sport)
                physical_score = calculate_physical_compatibility(user_data, sport_name, user_age)
                
                # Calcular habilidades técnicas
                tech_score = 50  # Default value
                if user_data.get('habilidades_tecnicas'):
                    tech_data = user_data['habilidades_tecnicas']
                    tech_scores = []
                    
                    # Coordenação (0-50)
                    if 'coordenacao' in tech_data:
                        coord_score = normalize_score(tech_data['coordenacao'], 0, 50)
                        tech_scores.append(coord_score)
                    
                    # Precisão (0-10)
                    if 'precisao' in tech_data:
                        prec_score = normalize_score(tech_data['precisao'], 0, 10)
                        tech_scores.append(prec_score)
                    
                    # Agilidade (5-15, inverso)
                    if 'agilidade' in tech_data:
                        agil_score = normalize_score(tech_data['agilidade'], 5, 15, inverse=True)
                        tech_scores.append(agil_score)
                    
                    # Equilíbrio (0-60)
                    if 'equilibrio' in tech_data:
                        equil_score = normalize_score(tech_data['equilibrio'], 0, 60)
                        tech_scores.append(equil_score)
                    
                    tech_score = np.mean(tech_scores) if tech_scores else 50

                # Calcular aspectos táticos
                tactic_score = 50
                if user_data.get('aspectos_taticos'):
                    tactic_data = user_data['aspectos_taticos']
                    tactic_scores = []
                    
                    for aspect in ['tomada_decisao', 'visao_jogo', 'posicionamento']:
                        if aspect in tactic_data:
                            score = normalize_score(tactic_data[aspect], 0, 10)
                            tactic_scores.append(score)
                    
                    if tactic_scores:
                        tactic_score = np.mean(tactic_scores)

                # Calcular score final com ajuste para idade
                base_score = (
                    biotype_score * 0.30 +    # Biotipo (30%)
                    physical_score * 0.25 +    # Físico (25%)
                    tech_score * 0.25 +        # Técnico (25%)
                    tactic_score * 0.20        # Tático (20%)
                ) * 0.7  # Score base máximo de 70%

                # Ajustes específicos
                if user_data.get('altura', 0) >= 180:
                    if any(s in sport_name.lower() for s in ['basketball', 'volleyball']):
                        base_score *= 1.1  # Bônus de 10% para esportes que valorizam altura
                
                # Ajuste baseado na idade
                age_factor = min(1.0, max(0.6, (user_age - 10) / 8))
                final_score = base_score * age_factor

                # Garantir que o score não ultrapasse 90%
                final_score = min(90, final_score)

                # Traduzir nome do esporte
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

        # Ordenar por compatibilidade
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
