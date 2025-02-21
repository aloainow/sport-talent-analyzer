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
    Traduz o nome completo do evento esportivo de inglês para português
    
    Args:
        sport_name (str): Nome do evento em inglês
        user_gender (str): Gênero do usuário ("Masculino" ou "Feminino")
    
    Returns:
        str: Nome do evento traduzido para português
    """
    # Primeiro, vamos substituir casos especiais e eventos completos
    FULL_EVENT_TRANSLATIONS = {
        "Art Competitions Mixed Sculpturing, Statues": "Competições de Arte Escultura Mista, Estátuas",
        "Gymnastics Team All-Around, Free System": "Ginástica Equipe Geral, Sistema Livre",
        "Athletics Men's 100 metres": "Atletismo 100 metros Masculino",
        "Athletics Women's 100 metres": "Atletismo 100 metros Feminino",
        "Swimming Men's 100 metres Freestyle": "Natação 100 metros Nado Livre Masculino",
        "Swimming Women's 100 metres Freestyle": "Natação 100 metros Nado Livre Feminino",
        "Basketball Men's Basketball": "Basquete Masculino",
        "Basketball Women's Basketball": "Basquete Feminino",
        "Volleyball Men's Volleyball": "Vôlei Masculino",
        "Volleyball Women's Volleyball": "Vôlei Feminino",
        # Adicione mais traduções completas conforme necessário
    }

    # Verifica se existe uma tradução completa para o evento
    if sport_name in FULL_EVENT_TRANSLATIONS:
        return FULL_EVENT_TRANSLATIONS[sport_name]

    # Se não houver tradução completa, traduz parte por parte
    translated_name = sport_name

    # Remove o gênero inicial (será adicionado no final)
    translated_name = translated_name.replace("Men's ", "").replace("Women's ", "")

    # Traduz cada parte usando o dicionário existente
    for en, pt in SPORTS_TRANSLATIONS.items():
        translated_name = translated_name.replace(en, pt)

    # Organiza a estrutura do nome
    parts = translated_name.split(',')
    main_parts = []
    
    for part in parts:
        # Remove espaços extras
        part = part.strip()
        
        # Trata a parte principal do nome
        subparts = part.split()
        
        # Remove palavras duplicadas
        subparts = list(dict.fromkeys(subparts))
        
        # Reorganiza na ordem do português
        if 'metros' in subparts:
            idx = subparts.index('metros')
            number = subparts[idx-1] if idx > 0 else ''
            event_type = ' '.join(subparts[idx+1:]) if idx < len(subparts)-1 else ''
            subparts = [number, 'metros', event_type]
            subparts = [p for p in subparts if p]  # Remove elementos vazios
            
        main_parts.append(' '.join(subparts))

    # Junta todas as partes
    translated_name = ', '.join(main_parts)

    # Adiciona o gênero no final
    if user_gender == "Masculino":
        translated_name += " Masculino"
    elif user_gender == "Feminino":
        translated_name += " Feminino"

    # Limpa espaços extras e formatação
    translated_name = ' '.join(translated_name.split())
    
    # Remove artigos desnecessários
    translated_name = translated_name.replace(" o ", " ").replace(" a ", " ").replace(" os ", " ").replace(" as ", " ")

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

                # Calcular score final com ajuste para idade
                base_score = (
                    biotype_score * 0.30 +    # Biotipo (30%)
                    physical_score * 0.25 +    # Físico (25%)
                    tech_score * 0.25 +        # Técnico (25%)
                    tactic_score * 0.20        # Tático (20%)
                ) * 0.7  # Score base máximo de 70%

                # Ajustes específicos
                if user_data.get('altura', 0) >= 200:  # Para atletas muito altos
                    if any(sport in sport_name.lower() for sport in ['basketball', 'volleyball']):
                        base_score *= 1.15  # Bônus de 15% para esportes que valorizam altura
                    elif any(sport in sport_name.lower() for sport in ['athletics', 'swimming']):
                        base_score *= 1.1   # Bônus de 10% para outros esportes onde altura ajuda

                # Ajuste baseado na idade
                age_factor = min(1.0, max(0.6, (user_age - 10) / 8))  # Fator cresce com a idade
                final_score = base_score * age_factor

                # Garantir que o score não ultrapasse 95%
                final_score = min(95, final_score)

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

        # Se não houver recomendações, usar padrão
        if not recommendations:
            st.warning("Nenhuma recomendação gerada. Usando sugestões padrão.")
            return get_recommendations_without_api(user_gender)

        # Ordenar por compatibilidade e retornar top 10
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
