import sys
import os
import streamlit as st
import pandas as pd
import json
import numpy as np
import openai
from typing import Dict, List, Any
from generate_translations import traduzir_evento, clean_event_name, get_base_sport_name

def load_and_process_data():
    """
    Carrega e processa os dados dos esportes do JSON
    """
    try:
        possible_paths = [
            'data/sport_profiles.json',
            './data/sport_profiles.json',
            os.path.join('data', 'sport_profiles.json'),
            'sport_profiles.json'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    sports_data = json.load(f)
                
                sports_list = []
                for sport in sports_data['sports']:
                    # Adicionando variações de eventos com gênero explícito
                    events = [
                        f"{sport['name']} Masculino",
                        f"{sport['name']} Feminino"
                    ]
                    
                    for event in events:
                        sports_list.append({
                            'Event': event,
                            'Category': sport['category'],
                            'Physical_Requirements': sport['requirements']['physical'],
                            'Technical_Requirements': sport['requirements']['technical'],
                            'Tactical_Requirements': sport['requirements']['tactical'],
                            'Psychological_Requirements': sport['requirements']['psychological'],
                            'Key_Attributes': sport['key_attributes']
                        })
                
                return pd.DataFrame(sports_list)
                
        st.error("❌ Arquivo sport_profiles.json não encontrado")
        return None
    
    except Exception as e:
        st.error(f"Erro ao carregar dados dos esportes: {str(e)}")
        return None

def normalize_score(value, min_val, max_val, inverse=False):
    """Normaliza um valor para escala 0-100"""
    try:
        if value is None or value == "":
            return 50.0
        value = float(value)
        if inverse:
            if value <= min_val:
                return 100.0
            elif value >= max_val:
                return 0.0
            return ((max_val - value) / (max_val - min_val)) * 100.0
        else:
            if value >= max_val:
                return 100.0
            elif value <= min_val:
                return 0.0
            return ((value - min_val) / (max_val - min_val)) * 100.0
    except (TypeError, ValueError):
        return 50.0

def calculate_physical_compatibility(user_data: Dict, sport_name: str, user_age: int = 18) -> float:
    """Calcula compatibilidade física baseada nos testes"""
    try:
        if not user_data or not user_data.get('dados_fisicos'):
            return 50.0
        
        dados_fisicos = user_data.get('dados_fisicos', {})
        
        velocidade = dados_fisicos.get('velocidade', 5.0)
        forca_superior = dados_fisicos.get('forca_superior', 0)
        forca_inferior = dados_fisicos.get('forca_inferior', 0)
        
        scores = []
        
        velocity_sports = ['Athletics', 'Swimming', 'Cycling', 'Sprint']
        if any(sport in sport_name for sport in velocity_sports):
            velocity_score = normalize_score(velocidade, 2.5, 5.0, inverse=True)
            scores.append(velocity_score * 1.5)
        
        strength_sports = ['Weightlifting', 'Wrestling', 'Judo', 'Boxing']
        if any(sport in sport_name for sport in strength_sports):
            strength_upper = normalize_score(forca_superior, 0, 50)
            strength_lower = normalize_score(forca_inferior, 0, 60)
            scores.extend([strength_upper * 1.5, strength_lower * 1.5])
            
        if not scores:
            return 50.0
            
        base_score = float(np.mean(scores))
        age_factor = min(1.0, max(0.6, (user_age - 10) / 8))
        
        return float(base_score * age_factor)
            
    except Exception as e:
        st.error(f"Erro no cálculo de compatibilidade física: {str(e)}")
        return 50.0

def calculate_biotype_compatibility(user_data: Dict, sport: pd.Series) -> float:
    """Calcula a compatibilidade do biotipo do usuário com o esporte"""
    try:
        if not user_data or not user_data.get('biotipo'):
            return 50.0
            
        biotype_data = user_data.get('biotipo', {})
        sport_name = sport['Event'].lower()
        
        scores = []
        
        altura = biotype_data.get('altura')
        if altura is not None:
            if any(s in sport_name for s in ['basketball', 'volleyball']):
                height_score = normalize_score(altura, 170, 210)
                scores.append(height_score * 1.5)
            elif any(s in sport_name for s in ['gymnastics', 'wrestling']):
                height_score = normalize_score(altura, 150, 180)
                scores.append(height_score)
        
        peso = biotype_data.get('peso')
        if peso is not None:
            if any(s in sport_name for s in ['boxing', 'wrestling', 'judo']):
                if 'heavyweight' in sport_name:
                    weight_score = normalize_score(peso, 80, 120)
                elif 'middleweight' in sport_name:
                    weight_score = normalize_score(peso, 70, 85)
                elif 'lightweight' in sport_name:
                    weight_score = normalize_score(peso, 50, 70)
                else:
                    weight_score = normalize_score(peso, 40, 120)
                scores.append(weight_score * 1.3)
        
        envergadura = biotype_data.get('envergadura')
        if envergadura is not None:
            if any(s in sport_name for s in ['swimming', 'boxing', 'basketball']):
                wingspan_score = normalize_score(envergadura, 170, 220)
                scores.append(wingspan_score * 1.2)
        
        if not scores:
            return 50.0
            
        return float(np.mean(scores))
        
    except Exception as e:
        st.warning(f"Erro no cálculo de compatibilidade de biotipo: {str(e)}")
        return 50.0

def calculate_technical_score(user_data: Dict) -> float:
    """Calcula score técnico do usuário"""
    if not user_data.get('habilidades_tecnicas'):
        return 50.0
        
    scores = []
    tech_data = user_data['habilidades_tecnicas']
    
    if 'coordenacao' in tech_data:
        scores.append(normalize_score(tech_data['coordenacao'], 0, 50))
    if 'precisao' in tech_data:
        scores.append(normalize_score(tech_data['precisao'], 0, 10))
    if 'agilidade' in tech_data:
        scores.append(normalize_score(tech_data['agilidade'], 5, 15, inverse=True))
    if 'equilibrio' in tech_data:
        scores.append(normalize_score(tech_data['equilibrio'], 0, 60))
        
    return float(np.mean(scores)) if scores else 50.0

def calculate_tactical_score(user_data: Dict) -> float:
    """Calcula score tático do usuário"""
    if not user_data.get('aspectos_taticos'):
        return 50.0
        
    scores = []
    tactic_data = user_data['aspectos_taticos']
    
    if 'tomada_decisao' in tactic_data:
        scores.append(normalize_score(tactic_data['tomada_decisao'], 0, 10))
    if 'visao_jogo' in tactic_data:
        scores.append(normalize_score(tactic_data['visao_jogo'], 0, 10))
    if 'posicionamento' in tactic_data:
        scores.append(normalize_score(tactic_data['posicionamento'], 1, 10))
        
    return float(np.mean(scores)) if scores else 50.0

def calculate_psychological_score(user_data: Dict) -> float:
    """Calcula score psicológico do usuário"""
    if not user_data.get('fatores_psicologicos'):
        return 50.0
        
    psych_data = user_data['fatores_psicologicos']
    scores = []
    
    if 'motivacao' in psych_data:
        mot_score = np.mean([
            psych_data['motivacao'].get('dedicacao', 5),
            psych_data['motivacao'].get('frequencia', 5),
            psych_data['motivacao'].get('comprometimento', 5)
        ])
        scores.append(normalize_score(mot_score, 1, 10))
    
    if 'resiliencia' in psych_data:
        res_score = np.mean([
            psych_data['resiliencia'].get('derrotas', 5),
            psych_data['resiliencia'].get('criticas', 5),
            psych_data['resiliencia'].get('erros', 5)
        ])
        scores.append(normalize_score(res_score, 1, 10))
    
    if 'trabalho_equipe' in psych_data:
        team_score = np.mean([
            psych_data['trabalho_equipe'].get('comunicacao', 5),
            psych_data['trabalho_equipe'].get('opinioes', 5),
            psych_data['trabalho_equipe'].get('contribuicao', 5)
        ])
        scores.append(normalize_score(team_score, 1, 10))
        
    return float(np.mean(scores)) if scores else 50.0

def calculate_base_score(biotype_score: float, physical_score: float, tech_score: float, 
                        tactic_score: float, psych_score: float, sport_name: str, 
                        user_data: Dict) -> float:
    """Calcula o score base considerando todos os fatores"""
    try:
        # Definir pesos baseados na relevância para cada tipo de esporte
        sport_type_weights = {
            'individual': {
                'biotype': 0.3,
                'physical': 0.25,
                'technical': 0.2,
                'tactical': 0.15,
                'psychological': 0.1
            },
            'collective': {
                'biotype': 0.2,
                'physical': 0.25,
                'technical': 0.2,
                'tactical': 0.2,
                'psychological': 0.15
            }
        }

        # Determinar o tipo de esporte
        sport_category = 'individual' if 'Individual' in sport_name else 'collective'
        weights = sport_type_weights[sport_category]
        
        # Calcular score base
        base_score = (
            biotype_score * weights['biotype'] +
            physical_score * weights['physical'] +
            tech_score * weights['technical'] +
            tactic_score * weights['tactical'] +
            psych_score * weights['psychological']
        ) * 2  # Multiplicar por 2 para dar mais amplitude
        
        # Fatores de ajuste específicos
        sport_name_lower = sport_name.lower()
        
        # Ajustes de compatibilidade específicos
        compatibilidade_ajustes = {
            'altura': {
                'esportes': ['basketball', 'volleyball'],
                'min_altura': 180,
                'fator_ajuste': 1.2
            },
            'forca': {
                'esportes': ['weightlifting', 'wrestling', 'boxing'],
                'min_forca': 40,
                'fator_ajuste': 1.15
            },
            'velocidade': {
                'esportes': ['athletics', 'swimming', 'cycling'],
                'max_velocidade': 3.5,
                'fator_ajuste': 1.15
            },
            'equilibrio': {
                'esportes': ['gymnastics'],
                'min_equilibrio': 50,
                'fator_ajuste': 1.15
            }
        }

        for ajuste, config in compatibilidade_ajustes.items():
            if any(s in sport_name_lower for s in config['esportes']):
                if ajuste == 'altura' and user_data['biotipo'].get('altura', 0) >= config['min_altura']:
                    base_score *= config['fator_ajuste']
                elif ajuste == 'forca' and user_data['dados_fisicos'].get('forca_superior', 0) >= config['min_forca']:
                    base_score *= config['fator_ajuste']
                elif ajuste == 'velocidade' and user_data['dados_fisicos'].get('velocidade', 5.0) <= config['max_velocidade']:
                    base_score *= config['fator_ajuste']
                elif ajuste == 'equilibrio' and user_data['habilidades_tecnicas'].get('equilibrio', 0) >= config['min_equilibrio']:
                    base_score *= config['fator_ajuste']
        
        # Ajuste por idade
        idade_fator = min(1.2, max(0.7, (user_data['idade'] - 10) / 6))
        base_score *= idade_fator
        
        # Normalizar entre 20 e 100
        return min(100, max(20, base_score))
        
    except Exception as e:
        st.warning(f"Erro no cálculo do score base: {str(e)}")
        return 50.0
def merge_sports_data(sports_data, olympic_data):
    """Combina os dados dos esportes com os dados olímpicos"""
    merged_data = []
    
    for _, sport in sports_data.iterrows():
        # Encontrar dados olímpicos correspondentes
        olympic_info = olympic_data[olympic_data['Event'].str.contains(sport['Event'], case=False, na=False)]
        
        if not olympic_info.empty:
            sport_dict = sport.to_dict()
            # Adicionar informações olímpicas
            sport_dict.update({
                'idade_media': olympic_info['idade_media'].mean(),
                'altura_media': olympic_info['altura_media'].mean(),
                'peso_media': olympic_info['peso_media'].mean(),
                'total_atletas': olympic_info['total_atletas'].sum()
            })
            merged_data.append(sport_dict)
            
    return pd.DataFrame(merged_data)

def evaluate_biometric_compatibility(user_data, sport_data):
    """Avalia a compatibilidade biométrica do atleta com o esporte"""
    score = 100
    
    # Verificar altura
    if 'altura_media' in sport_data and sport_data['altura_media'] > 0:
        altura_diff = abs(user_data['biotipo']['altura'] - sport_data['altura_media'])
        if altura_diff > 20:
            score -= 20
        elif altura_diff > 10:
            score -= 10
            
    # Verificar peso
    if 'peso_media' in sport_data and sport_data['peso_media'] > 0:
        peso_diff = abs(user_data['biotipo']['peso'] - sport_data['peso_media'])
        if peso_diff > 20:
            score -= 20
        elif peso_diff > 10:
            score -= 10
            
    # Verificar idade
    if 'idade_media' in sport_data and sport_data['idade_media'] > 0:
        idade_diff = abs(user_data['idade'] - sport_data['idade_media'])
        if idade_diff > 5:
            score -= 15
        elif idade_diff > 3:
            score -= 5
            
    return max(0, score)

def calculate_biometric_compatibility(user_data: Dict, event: Dict) -> float:
    """Calcula a compatibilidade biométrica do usuário com o evento"""
    score = 100
    
    # Altura
    if event['altura_media'] and not pd.isna(event['altura_media']):
        altura_diff = abs(user_data['biotipo']['altura'] - event['altura_media'])
        if altura_diff > 20:
            score -= 20
        elif altura_diff > 10:
            score -= 10
    
    # Peso
    if event['peso_media'] and not pd.isna(event['peso_media']):
        peso_diff = abs(user_data['biotipo']['peso'] - event['peso_media'])
        if peso_diff > 20:
            score -= 20
        elif peso_diff > 10:
            score -= 10
    
    # Idade
    if event['idade_media'] and not pd.isna(event['idade_media']):
        idade_diff = abs(user_data['idade'] - event['idade_media'])
        if idade_diff > 5:
            score -= 15
        elif idade_diff > 3:
            score -= 5
    
    return max(0, score)
    
def clean_json_response(response_str: str) -> str:
    """Limpa a resposta do GPT para extrair apenas o JSON válido"""
    # Remover marcadores de código markdown
    response_str = response_str.replace('```json', '').replace('```', '')
    
    # Encontrar o início e fim do JSON
    start_idx = response_str.find('{')
    end_idx = response_str.rfind('}') + 1
    
    if start_idx != -1 and end_idx != -1:
        return response_str[start_idx:end_idx]
    return response_str

def process_events_batch(filtered_events, user_data, batch_size=100):
    """Processa um lote de eventos e retorna as recomendações"""
    try:
        st.write(f"Processando {len(filtered_events)} eventos...")
        all_recommendations = []
        
        # Processar eventos em lotes
        for start_idx in range(0, len(filtered_events), batch_size):
            end_idx = start_idx + batch_size
            batch_events = filtered_events.iloc[start_idx:end_idx]
            
            # Para cada evento no lote, calcular score de compatibilidade
            for _, event in batch_events.iterrows():
                try:
                    # Calcular compatibilidade biométrica
                    altura_diff = abs(user_data['biotipo']['altura'] - event['altura_media'])
                    peso_diff = abs(user_data['biotipo']['peso'] - event['peso_media'])
                    idade_diff = abs(user_data['idade'] - event['idade_media'])
                    
                    # Calcular score base
                    biometric_score = 100
                    if altura_diff > 20: biometric_score -= 20
                    if peso_diff > 20: biometric_score -= 20
                    if idade_diff > 5: biometric_score -= 20
                    
                    # Ajustar score baseado em requisitos físicos específicos
                    evento_nome = event['Event'].lower()
                    
                    # Velocidade é importante
                    if any(x in evento_nome for x in ['sprint', 'running', '100m', '200m']):
                        if user_data['dados_fisicos']['velocidade'] < 3.5:
                            biometric_score += 20
                        elif user_data['dados_fisicos']['velocidade'] > 4.5:
                            biometric_score -= 20
                    
                    # Força é importante
                    if any(x in evento_nome for x in ['throw', 'weightlifting', 'shot put']):
                        if user_data['dados_fisicos']['forca_superior'] > 40:
                            biometric_score += 20
                    
                    # Equilíbrio é importante
                    if any(x in evento_nome for x in ['gymnastics', 'beam', 'balance']):
                        if user_data['habilidades_tecnicas']['equilibrio'] > 50:
                            biometric_score += 20
                    
                    # Adicionar à lista de recomendações
                    if biometric_score >= 70:  # Filtrar apenas eventos com boa compatibilidade
                        all_recommendations.append({
                            'name': traduzir_evento(event['Event']),
                            'compatibility': biometric_score,
                            'olympic_data': {
                                'idade_media': float(event['idade_media']),
                                'altura_media': float(event['altura_media']),
                                'peso_media': float(event['peso_media']),
                                'total_atletas': int(event['total_atletas'])
                            }
                        })
                except Exception as e:
                    st.warning(f"Erro ao processar evento {event['Event']}: {str(e)}")
                    continue
                    
        st.write(f"Encontrados {len(all_recommendations)} eventos compatíveis.")
        return all_recommendations
        
    except Exception as e:
        st.error(f"Erro no processamento dos eventos: {str(e)}")
        return []

def get_sport_recommendations(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Gera recomendações de eventos esportivos considerando todos os eventos"""
    try:
        st.write("Iniciando análise de recomendações...")
        
        # Carregar dados olímpicos
        olympic_data = pd.read_csv('data/perfil_eventos_olimpicos_verao.csv')
        st.write(f"Dados olímpicos carregados: {len(olympic_data)} eventos.")
        
        # Filtrar eventos por gênero
        gender_key = "Men's" if user_data['genero'] == "Masculino" else "Women's"
        gender_pt = "Masculino" if user_data['genero'] == "Masculino" else "Feminino"
        filtered_events = olympic_data[olympic_data['Event'].str.contains(gender_key)]
        
        # Agrupar eventos por modalidade esportiva base
        base_sports = {}
        for idx, event in filtered_events.iterrows():
            event_data = event.to_dict()  # Converter Series para dictionary
            sport_name = get_base_sport_name(event_data['Event'])
            if sport_name not in base_sports:
                base_sports[sport_name] = []
            base_sports[sport_name].append(event_data)
            
        all_recommendations = []
        
        # Processar cada modalidade esportiva
        for sport_name, events in base_sports.items():
            best_event = None
            best_score = 0
            
            for event in events:
                # Calcular score para o evento
                biometric_score = calculate_biometric_compatibility(user_data, event)
                physical_score = calculate_physical_compatibility(user_data, event['Event'])
                technical_score = calculate_technical_score(user_data)
                
                # Score final ponderado
                final_score = (biometric_score * 0.4 + physical_score * 0.3 + technical_score * 0.3)
                
                if final_score > best_score:
                    best_score = final_score
                    best_event = event
            
            if best_event is not None and best_score >= 70:
                # Gerar pontos fortes específicos
                strengths = []
                sport_pt = traduzir_evento(sport_name).replace(" Masculino", "").replace(" Feminino", "")
                
                # Análise física
                if user_data['dados_fisicos']['velocidade'] < 4.0:
                    strengths.append(f"Velocidade excepcional para {sport_pt}")
                if user_data['dados_fisicos']['forca_superior'] > 30:
                    strengths.append(f"Força adequada para {sport_pt}")
                    
                # Análise técnica
                if user_data['habilidades_tecnicas']['coordenacao'] > 35:
                    strengths.append(f"Boa coordenação motora para {sport_pt}")
                if user_data['habilidades_tecnicas']['equilibrio'] > 45:
                    strengths.append(f"Equilíbrio adequado para {sport_pt}")
                if user_data['habilidades_tecnicas']['precisao'] > 7:
                    strengths.append(f"Precisão técnica para {sport_pt}")
                    
                # Análise tática
                if user_data['aspectos_taticos']['tomada_decisao'] > 7:
                    strengths.append(f"Boa tomada de decisão para {sport_pt}")
                if user_data['aspectos_taticos']['visao_jogo'] > 7:
                    strengths.append(f"Visão de jogo desenvolvida para {sport_pt}")
                    
                # Análise psicológica
                if user_data['fatores_psicologicos']['motivacao']['comprometimento'] > 7:
                    strengths.append(f"Alto comprometimento necessário em {sport_pt}")
                
                # Garantir pelo menos 3 pontos fortes
                while len(strengths) < 3:
                    strengths.append(f"Potencial físico para {sport_pt}")
                
                # Áreas para desenvolver
                development = []
                
                if user_data['dados_fisicos']['velocidade'] > 4.0:
                    development.append("Melhorar velocidade")
                if user_data['dados_fisicos']['forca_superior'] < 30:
                    development.append("Desenvolver força superior")
                if user_data['habilidades_tecnicas']['coordenacao'] < 35:
                    development.append("Aprimorar coordenação motora")
                if user_data['habilidades_tecnicas']['precisao'] < 7:
                    development.append("Trabalhar precisão técnica")
                if user_data['aspectos_taticos']['tomada_decisao'] < 7:
                    development.append("Desenvolver tomada de decisão")
                    
                # Garantir pelo menos 3 áreas de desenvolvimento
                while len(development) < 3:
                    development.append("Aprimoramento técnico específico")
                
                # Adicionar recomendação
                recommendation = {
                    'name': traduzir_evento(best_event['Event']),
                    'compatibility': round(min(100, best_score), 2),  # Arredondar para 2 casas decimais
                    'strengths': strengths[:3],  # Pegar os 3 principais pontos fortes
                    'development': development[:3],  # Pegar as 3 principais áreas
                    'olympic_data': {
                        'idade_media': float(best_event['idade_media']),
                        'altura_media': float(best_event['altura_media']),
                        'peso_media': float(best_event['peso_media']),
                        'total_atletas': int(best_event['total_atletas'])
                    }
                }
                all_recommendations.append(recommendation)
        
        # Ordenar por compatibilidade e pegar os top 5
        all_recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
        final_recommendations = all_recommendations[:5]
        
        # Ajustar compatibilidade para ter variação
        if final_recommendations:
            max_compat = final_recommendations[0]['compatibility']
            for i, rec in enumerate(final_recommendations):
                rec['compatibility'] = round(max(70, min(100, max_compat - (i * 5))), 2)
        
        # Se não houver recomendações suficientes, adicionar mais opções
        while len(final_recommendations) < 5 and len(all_recommendations) > 0:
            final_recommendations.append(all_recommendations[0])
            all_recommendations = all_recommendations[1:]
        
        if not final_recommendations:
            st.warning("Não foram encontradas recomendações que atendam aos critérios mínimos.")
            return []
            
        return final_recommendations

    except Exception as e:
        st.error(f"Erro na recomendação de esportes: {str(e)}")
        import traceback
        st.error(f"Detalhes do erro: {traceback.format_exc()}")
        return []
def get_sport_strengths(sport_name: str, user_data: Dict) -> List[str]:
    """Identifica os pontos fortes do usuário para um determinado esporte"""
    try:
        strengths = []
        sport_name = sport_name.lower()
        
        # Biotipo
        if user_data.get('biotipo'):
            altura = user_data['biotipo'].get('altura', 0)
            peso = user_data['biotipo'].get('peso', 0)
            envergadura = user_data['biotipo'].get('envergadura', 0)
            
            if altura >= 180 and any(s in sport_name for s in ['basketball', 'volleyball']):
                strengths.append("Altura favorável para esportes de altura")
            if envergadura >= 190 and any(s in sport_name for s in ['swimming', 'boxing']):
                strengths.append("Envergadura excelente")
            if peso >= 80 and any(s in sport_name for s in ['rugby', 'wrestling']):
                strengths.append("Biotipo favorável para esportes de força")
        
        # Dados físicos
        if user_data.get('dados_fisicos'):
            velocidade = user_data['dados_fisicos'].get('velocidade', 0)
            forca_superior = user_data['dados_fisicos'].get('forca_superior', 0)
            forca_inferior = user_data['dados_fisicos'].get('forca_inferior', 0)
            
            if velocidade <= 3.5:
                strengths.append("Velocidade excepcional")
            if forca_superior >= 40:
                strengths.append("Força superior desenvolvida")
            if forca_inferior >= 50:
                strengths.append("Força inferior potente")
            
        # Habilidades técnicas
        if user_data.get('habilidades_tecnicas'):
            coordenacao = user_data['habilidades_tecnicas'].get('coordenacao', 0)
            precisao = user_data['habilidades_tecnicas'].get('precisao', 0)
            equilibrio = user_data['habilidades_tecnicas'].get('equilibrio', 0)
            
            if coordenacao >= 40:
                strengths.append("Coordenação motora avançada")
            if precisao >= 8:
                strengths.append("Alta precisão técnica")
            if equilibrio >= 50:
                strengths.append("Equilíbrio corporal excecional")
        
        # Aspectos táticos
        if user_data.get('aspectos_taticos'):
            tomada_decisao = user_data['aspectos_taticos'].get('tomada_decisao', 0)
            visao_jogo = user_data['aspectos_taticos'].get('visao_jogo', 0)
            
            if tomada_decisao >= 8:
                strengths.append("Tomada de decisão rápida")
            if visao_jogo >= 8:
                strengths.append("Excelente visão estratégica")
        
        # Fatores psicológicos
        if user_data.get('fatores_psicologicos'):
            motivacao = user_data['fatores_psicologicos'].get('motivacao', {})
            resiliencia = user_data['fatores_psicologicos'].get('resiliencia', {})
            
            if motivacao.get('comprometimento', 0) >= 8:
                strengths.append("Alto comprometimento")
            if resiliencia.get('erros', 0) >= 8:
                strengths.append("Resiliência em situações de pressão")
        
        # Retorna os 3 principais pontos fortes
        return strengths[:3] if strengths else ["Necessita avaliação completa"]
        
    except Exception as e:
        st.warning(f"Erro ao identificar pontos fortes: {str(e)}")
        return ["Necessita avaliação completa"]
def get_development_areas(sport_name: str, user_data: Dict) -> List[str]:
    """Identifica áreas de desenvolvimento para um determinado esporte"""
    try:
        areas = []
        sport_name = sport_name.lower()
        
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
