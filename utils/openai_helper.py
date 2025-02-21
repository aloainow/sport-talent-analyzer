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
        altura_min = sport_data.get('altura_min')
        altura_max = sport_data.get('altura_max')
        
        # Verificar se os valores são válidos antes de calcular
        if altura_min is not None and altura_max is not None and height is not None:
            try:
                altura_min = float(altura_min)
                altura_max = float(altura_max)
                height = float(height)
                
                height_score = normalize_score(height, altura_min, altura_max)
                if altura_min <= height <= altura_max:
                    height_score += 20
                scores.append(height_score)
            except (ValueError, TypeError):
                scores.append(50)
        else:
            scores.append(50)
    
    # Peso
    if 'peso' in user_data:
        weight = user_data['peso']
        peso_min = sport_data.get('peso_min')
        peso_max = sport_data.get('peso_max')
        
        if peso_min is not None and peso_max is not None and weight is not None:
            try:
                peso_min = float(peso_min)
                peso_max = float(peso_max)
                weight = float(weight)
                
                weight_score = normalize_score(weight, peso_min, peso_max)
                if peso_min <= weight <= peso_max:
                    weight_score += 20
                scores.append(weight_score)
            except (ValueError, TypeError):
                scores.append(50)
        else:
            scores.append(50)
    
    return np.mean(scores) if scores else 50

def calculate_physical_compatibility(user_data: Dict, sport_name: str, user_age: int = 18) -> float:
    """
    Calcula compatibilidade física baseada nos testes, ajustada pela idade
    """
    try:
        if not user_data.get('dados_fisicos'):
            return 50
            
        scores = []
        gender = user_data.get('genero', 'Masculino')
        
        # Velocidade (esportes que valorizam velocidade)
        velocity_sports = ['Athletics', 'Swimming', 'Cycling', 'Sprint']
        if any(sport in sport_name for sport in velocity_sports):
            try:
                velocity_score = normalize_score(
                    user_data['dados_fisicos'].get('velocidade', 5),
                    2.5, 5.0, inverse=True
                )
                scores.append(velocity_score * 1.5)
            except Exception as e:
                st.warning(f"Erro ao calcular score de velocidade: {str(e)}")
        
        # Força (esportes que valorizam força)
        strength_sports = ['Weightlifting', 'Wrestling', 'Judo', 'Boxing']
        if any(sport in sport_name for sport in strength_sports):
            try:
                strength_upper = normalize_score(
                    user_data['dados_fisicos'].get('forca_superior', 0),
                    0, 50
                )
                strength_lower = normalize_score(
                    user_data['dados_fisicos'].get('forca_inferior', 0),
                    0, 60
                )
                scores.extend([strength_upper * 1.5, strength_lower * 1.5])
            except Exception as e:
                st.warning(f"Erro ao calcular scores de força: {str(e)}")
        
        # Calcular média dos scores disponíveis
        if not scores:
            return 50
            
        base_score = np.mean(scores)
        
        # Ajuste baseado na idade
        try:
            age_factor = min(1.0, max(0.6, (user_age - 10) / 8))
            return base_score * age_factor
        except Exception as e:
            st.warning(f"Erro ao ajustar score por idade: {str(e)}")
            return base_score
            
    except Exception as e:
        st.error(f"Erro no cálculo de compatibilidade física: {str(e)}")
        return 50    
# Dicionário de traduções de esportes
SPORTS_TRANSLATIONS = {
    # Atletismo
    "Athletics": "Atletismo",
    "metres": "metros",
    "Hurdles": "com Barreiras",
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
    "Road Race": "Corrida de Estrada",
    "Individual": "Individual"
}

def translate_sport_name(sport_name: str, user_gender: str) -> str:
    """
    Traduz o nome do esporte de inglês para português e adiciona o gênero apropriado
    
    Args:
        sport_name (str): Nome do esporte em inglês
        user_gender (str): Gênero do usuário ("Masculino" ou "Feminino")
    
    Returns:
        str: Nome do esporte traduzido com gênero apropriado
    """
    translated_name = sport_name
    
    # Substituir cada termo em inglês pelo seu equivalente em português
    for en, pt in SPORTS_TRANSLATIONS.items():
        translated_name = translated_name.replace(en, pt)
    
    # Ajustar a formatação para ficar mais natural em português
    parts = translated_name.split(', ')  # Divide por vírgula para preservar a estrutura
    
    # Para cada parte do nome
    for i, part in enumerate(parts):
        subparts = part.split()
        # Remove termos de gênero existentes
        subparts = [p for p in subparts if p not in ["Masculino", "Feminino"]]
        # Reconstrói a parte
        parts[i] = " ".join(subparts)
    
    # Junta as partes novamente com vírgula
    translated_name = ", ".join(parts)
    
    # Adiciona o gênero como sufixo
    if user_gender == "Masculino":
        translated_name += " Masculino"
    elif user_gender == "Feminino":
        translated_name += " Feminino"
    
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
        strengths.insert(0, "Altura Excepcional")
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
    
    return strengths[:3]

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
            areas.append("Posicionamento")
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
    
    return areas[:3]

def get_sport_recommendations(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Gera recomendações de esportes baseadas nos dados do usuário e estatísticas olímpicas
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

        # Obter dados básicos do usuário com validação
        user_gender = user_data.get('genero', '')
        user_age = user_data.get('idade', 18)  

        try:
            # Carregar módulo de cálculos ajustados por idade
            from utils.age_adjusted_calculations import (
                calculate_age_adjusted_score,
                get_age_group
            )
        except ImportError as e:
            st.error(f"Erro ao importar módulo de cálculos: {str(e)}")
            return get_recommendations_without_api(user_data.get('genero', 'Masculino'))

        # Filtrar eventos por gênero com validação
        try:
            if user_gender == "Masculino":
                sports_data = sports_data[
                    (~sports_data['Event'].str.contains("Women", case=False)) &
                    (sports_data['Event'].str.contains("Men", case=False) | 
                     ~sports_data['Event'].str.contains("Women|Men", case=False))
                ]
            elif user_gender == "Feminino":
                sports_data = sports_data[sports_data['Event'].str.contains("Women", case=False)]

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
                tech_score = 50
                if user_data.get('habilidades_tecnicas'):
                    tech_data = user_data['habilidades_tecnicas']
                    tech_scores = []
                    
                    # Coordenação
                    if 'coordenacao' in tech_data:
                        tech_scores.append(normalize_score(tech_data['coordenacao'], 0, 50))
                    # Precisão
                    if 'precisao' in tech_data:
                        tech_scores.append(normalize_score(tech_data['precisao'], 0, 10))
                    # Agilidade
                    if 'agilidade' in tech_data:
                        tech_scores.append(normalize_score(tech_data['agilidade'], 5, 15, inverse=True))
                    
                    if tech_scores:
                        tech_score = np.mean(tech_scores)

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

                # Calcular score final
                base_score = (
                    biotype_score * 0.30 +    # Biotipo (30%)
                    physical_score * 0.25 +    # Físico (25%)
                    tech_score * 0.25 +        # Técnico (25%)
                    tactic_score * 0.20        # Tático (20%)
                ) * 0.8  # Ajuste para escala mais realista

                # Ajustes específicos
                if user_data.get('altura', 0) >= 200:
                    if any(s in sport_name.lower() for s in ['basketball', 'volleyball']):
                        base_score *= 1.15

                final_score = min(100, base_score)

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

        # Ordenar e retornar recomendações
        if not recommendations:
            st.warning("Nenhuma recomendação gerada. Usando sugestões padrão.")
            return get_recommendations_without_api(user_gender)

        recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
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
