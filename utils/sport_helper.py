import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import json
import numpy as np
from typing import Dict, List, Any

from utils.test_processor import normalize_score, calculate_average
from utils.age_adjusted_calculations import get_age_group

# Importações locais
from .test_processor import normalize_score, calculate_average
from .age_adjusted_calculations import get_age_group

def normalize_score(value, min_val, max_val, inverse=False):
    """Normaliza um valor para escala 0-100"""
    try:
        if value is None or value == "":  # Adicionado para evitar NoneType
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


# Dicionário de traduções de eventos completos (mantido do código original)
EVENT_TRANSLATIONS = {
    # Será substituído pelo conteúdo gerado pelo script de tradução
}
def load_and_process_data():
    """
    Carrega e processa os dados dos esportes do JSON
    """
    try:
        # Lista de possíveis caminhos para o arquivo JSON
        possible_paths = [
            'data/sport_profiles.json',
            './data/sport_profiles.json',
            os.path.join('data', 'sport_profiles.json'),
            'sport_profiles.json'
        ]
        
        # Tenta carregar o arquivo de diferentes locais
        for path in possible_paths:
            if os.path.exists(path):
                st.write(f"📁 Carregando arquivo JSON de: {path}")
                with open(path, 'r', encoding='utf-8') as f:
                    sports_data = json.load(f)
                
                # Converter para DataFrame
                sports_list = []
                for sport in sports_data['sports']:
                    sports_list.append({
                        'Event': sport['name'],
                        'Category': sport['category'],
                        'Physical_Requirements': sport['requirements']['physical'],
                        'Technical_Requirements': sport['requirements']['technical'],
                        'Tactical_Requirements': sport['requirements']['tactical'],
                        'Psychological_Requirements': sport['requirements']['psychological'],
                        'Key_Attributes': sport['key_attributes']
                    })
                
                return pd.DataFrame(sports_list)
                
        # Se nenhum arquivo for encontrado, mostra erro
        st.error("❌ Arquivo sport_profiles.json não encontrado")
        return None
    
    except Exception as e:
        st.error(f"Erro ao carregar dados dos esportes: {str(e)}")
        return None
        
def data_sports_default():
    """
    Dados padrão de esportes caso o CSV não seja encontrado
    """
    return {
        'Event': [
            "Athletics Men's 100 metres",
            "Swimming Men's 100 metres Freestyle",
            "Gymnastics Men's Floor Exercise",
            "Basketball Men's Basketball",
            "Volleyball Men's Volleyball"
        ]
    }

def calculate_physical_compatibility(user_data: Dict, sport_name: str, user_age: int = 18) -> float:
    """
    Calcula compatibilidade física baseada nos testes, ajustada pela idade
    """
    try:
        # Verificação de dados de entrada
        if not user_data or not user_data.get('dados_fisicos'):
            st.warning("Dados físicos não disponíveis. Retornando compatibilidade padrão.")
            return 50.0
        
        dados_fisicos = user_data.get('dados_fisicos', {})
        
        # Verificar e definir valores padrão se não existirem
        velocidade = dados_fisicos.get('velocidade', 5.0)
        forca_superior = dados_fisicos.get('forca_superior', 0)
        forca_inferior = dados_fisicos.get('forca_inferior', 0)
        
        # Inicializar lista de scores
        scores = []
        
        # Substituir verificações por uma função mais robusta
        def safe_normalize_score(value, min_val, max_val, inverse=False):
            try:
                if value is None:
                    return 50.0  # Valor padrão
                return normalize_score(value, min_val, max_val, inverse)
            except Exception:
                return 50.0
        
        # Velocidade (esportes que valorizam velocidade)
        velocity_sports = ['Athletics', 'Swimming', 'Cycling', 'Sprint']
        if any(sport in sport_name for sport in velocity_sports):
            velocity_score = safe_normalize_score(velocidade, 2.5, 5.0, inverse=True)
            scores.append(velocity_score * 1.5)
        
        # Força (esportes que valorizam força)
        strength_sports = ['Weightlifting', 'Wrestling', 'Judo', 'Boxing']
        if any(sport in sport_name for sport in strength_sports):
            strength_upper = safe_normalize_score(forca_superior, 0, 50)
            strength_lower = safe_normalize_score(forca_inferior, 0, 60)
            scores.extend([strength_upper * 1.5, strength_lower * 1.5])
        
        # Calcular média dos scores disponíveis
        if not scores:
            return 50.0
            
        base_score = float(np.mean(scores))
        
        # Ajuste baseado na idade
        age_factor = min(1.0, max(0.6, (user_age - 10) / 8))
        
        # Retornar score final como float
        return float(base_score * age_factor)
            
    except Exception as e:
        st.error(f"Erro no cálculo de compatibilidade física: {str(e)}")
        return 50.0

def calculate_biotype_compatibility(user_data: Dict, sport: pd.Series) -> float:
    """
    Calcula a compatibilidade do biotipo do usuário com o esporte
    """
    try:
        # Verificação de dados de entrada
        if not user_data or not user_data.get('biotipo'):
            st.warning("Dados de biotipo não disponíveis. Retornando compatibilidade padrão.")
            return 50.0
            
        biotype_data = user_data.get('biotipo', {})
        sport_name = sport['Event'].lower()
        
        # Função para normalização segura
        def safe_normalize_score(value, min_val, max_val):
            try:
                if value is None:
                    return 50.0  # Valor padrão
                return normalize_score(value, min_val, max_val)
            except Exception:
                return 50.0
        
        # Inicializar lista de scores
        scores = []
        
        # Altura (150-220 cm)
        altura = biotype_data.get('altura')
        if altura is not None:
            # Esportes que valorizam altura
            if any(s in sport_name for s in ['basketball', 'volleyball']):
                height_score = safe_normalize_score(altura, 170, 210)
                scores.append(height_score * 1.5)  # Peso maior para altura
            
            # Esportes que valorizam altura média/baixa
            elif any(s in sport_name for s in ['gymnastics', 'wrestling']):
                height_score = safe_normalize_score(altura, 150, 180)
                scores.append(height_score)
        
        # Peso (40-120 kg)
        peso = biotype_data.get('peso')
        if peso is not None:
            # Categorias de peso para esportes de combate
            if any(s in sport_name for s in ['boxing', 'wrestling', 'judo']):
                # Simplificação das categorias de peso
                if 'heavyweight' in sport_name:
                    weight_score = safe_normalize_score(peso, 80, 120)
                elif 'middleweight' in sport_name:
                    weight_score = safe_normalize_score(peso, 70, 85)
                elif 'lightweight' in sport_name:
                    weight_score = safe_normalize_score(peso, 50, 70)
                else:
                    weight_score = safe_normalize_score(peso, 40, 120)
                scores.append(weight_score * 1.3)
        
        # Envergadura (150-220 cm)
        envergadura = biotype_data.get('envergadura')
        if envergadura is not None:
            # Esportes que valorizam envergadura
            if any(s in sport_name for s in ['swimming', 'boxing', 'basketball']):
                wingspan_score = safe_normalize_score(envergadura, 170, 220)
                scores.append(wingspan_score * 1.2)
        
        # Se não houver scores, retorna valor padrão
        if not scores:
            return 50.0
            
        # Retorna média dos scores como float
        return float(np.mean(scores))
        
    except Exception as e:
        st.warning(f"Erro no cálculo de compatibilidade de biotipo: {str(e)}")
        return 50.0

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

def get_sport_strengths(sport_name: str, user_data: Dict) -> List[str]:
    """Identifica os pontos fortes do usuário para um determinado esporte"""
    strengths = []
    sport_name = sport_name.lower()
    
    try:
        # Biotipo
        if user_data.get('biotipo'):
            altura = user_data['biotipo'].get('altura', 0)
            peso = user_data['biotipo'].get('peso', 0)
            envergadura = user_data['biotipo'].get('envergadura', 0)
            
            if altura >= 180 and any(s in sport_name for s in ['basketball', 'volleyball']):
                strengths.append("Altura favorável")
            if envergadura >= 190 and any(s in sport_name for s in ['swimming', 'boxing']):
                strengths.append("Boa envergadura")
        
        # Dados físicos
        if user_data.get('dados_fisicos'):
            velocidade = user_data['dados_fisicos'].get('velocidade', 0)
            forca_superior = user_data['dados_fisicos'].get('forca_superior', 0)
            forca_inferior = user_data['dados_fisicos'].get('forca_inferior', 0)
            
            if velocidade <= 3.5 and any(s in sport_name for s in ['athletics', 'swimming']):
                strengths.append("Velocidade")
            if forca_superior >= 40:
                strengths.append("Força superior")
            if forca_inferior >= 50:
                strengths.append("Força inferior")
        
        # Habilidades técnicas
        if user_data.get('habilidades_tecnicas'):
            coordenacao = user_data['habilidades_tecnicas'].get('coordenacao', 0)
            precisao = user_data['habilidades_tecnicas'].get('precisao', 0)
            equilibrio = user_data['habilidades_tecnicas'].get('equilibrio', 0)
            
            if coordenacao >= 40:
                strengths.append("Coordenação")
            if precisao >= 8:
                strengths.append("Precisão")
            if equilibrio >= 50:
                strengths.append("Equilíbrio")
        
        # Retorna os 3 principais pontos fortes
        return strengths[:3] if strengths else ["Necessita avaliação completa"]
        
    except Exception as e:
        st.warning(f"Erro ao identificar pontos fortes: {str(e)}")
        return ["Necessita avaliação completa"]

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

def get_sport_recommendations(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Gera recomendações de esportes baseadas nos dados do usuário
    """
    try:
        # Estruturar corretamente os dados do usuário
        user_data = {
            'genero': st.session_state.personal_info.get('genero', 'Masculino'),
            'idade': st.session_state.personal_info.get('idade', 18),
            'biotipo': {
                'altura': st.session_state.personal_info.get('altura', 170),
                'peso': st.session_state.personal_info.get('peso', 60),
                'envergadura': st.session_state.personal_info.get('envergadura', 170)
            },
            'dados_fisicos': st.session_state.test_results.get('dados_fisicos', {}),
            'habilidades_tecnicas': st.session_state.test_results.get('habilidades_tecnicas', {}),
            'aspectos_taticos': st.session_state.test_results.get('aspectos_taticos', {}),
            'fatores_psicologicos': st.session_state.test_results.get('fatores_psicologicos', {})
        }

        # Verificar se todos os testes foram completados
        missing_tests = [
            key.replace('_', ' ').title() 
            for key in ['dados_fisicos', 'habilidades_tecnicas', 'aspectos_taticos', 'fatores_psicologicos'] 
            if not user_data[key]
        ]
        
        if missing_tests:
            st.error(f"Por favor, complete os seguintes testes: {', '.join(missing_tests)}")
            return []

        # Carregar dados dos esportes
        sports_data = load_and_process_data()
        if sports_data is None or sports_data.empty:
            st.error("Erro ao carregar dados dos esportes. Por favor, tente novamente mais tarde.")
            return []

        # Filtrar esportes por gênero
        if user_data['genero'] == "Feminino":
            sports_data = sports_data[sports_data['Event'].str.contains("Women's", case=False, na=False)]
        else:
            sports_data = sports_data[sports_data['Event'].str.contains("Men's", case=False, na=False)]

        if sports_data.empty:
            st.error(f"Não foram encontrados esportes para o gênero {user_data['genero']}")
            return []

        recommendations = []
        processed_sports = 0
        errors = 0

        for _, sport in sports_data.iterrows():
            try:
                sport_name = sport['Event']
                
                # Calcular scores individuais
                biotype_score = calculate_biotype_compatibility(user_data, sport)
                physical_score = calculate_physical_compatibility(user_data, sport_name, user_data['idade'])
                tech_score = calculate_technical_score(user_data)
                tactic_score = calculate_tactical_score(user_data)
                psych_score = calculate_psychological_score(user_data)

                # Calcular score base
                base_score = calculate_base_score(
                    biotype_score, physical_score, tech_score, 
                    tactic_score, psych_score, sport_name, user_data
                )

                # Traduzir nome do esporte
                translated_name = translate_sport_name(sport_name, user_data['genero'])

                # Gerar pontos fortes e áreas de desenvolvimento
                strengths = get_sport_strengths(sport_name, user_data)
                development = get_development_areas(sport_name, user_data)

                recommendations.append({
                    "name": translated_name,
                    "compatibility": round(base_score),
                    "strengths": strengths,
                    "development": development
                })
                processed_sports += 1

            except Exception as sport_e:
                errors += 1
                st.warning(f"Erro ao processar esporte {sport_name}: {str(sport_e)}")
                continue

        if not recommendations:
            st.error("Não foi possível gerar recomendações. Por favor, verifique seus dados e tente novamente.")
            return []

        if errors > 0:
            st.warning(f"Alguns esportes ({errors}) não puderam ser processados, mas encontramos {processed_sports} recomendações para você.")

        # Ordenar recomendações
        recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
        return recommendations[:10]

    except Exception as e:
        st.error(f"Erro inesperado ao gerar recomendações: {str(e)}")
        return []
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
    
    # Motivação
    if 'motivacao' in psych_data:
        mot_score = np.mean([
            psych_data['motivacao'].get('dedicacao', 5),
            psych_data['motivacao'].get('frequencia', 5),
            psych_data['motivacao'].get('comprometimento', 5)
        ])
        scores.append(normalize_score(mot_score, 1, 10))
    
    # Resiliência
    if 'resiliencia' in psych_data:
        res_score = np.mean([
            psych_data['resiliencia'].get('derrotas', 5),
            psych_data['resiliencia'].get('criticas', 5),
            psych_data['resiliencia'].get('erros', 5)
        ])
        scores.append(normalize_score(res_score, 1, 10))
    
    # Trabalho em equipe
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
        # Pesos base para cada componente
        weights = {
            'biotype': 0.25,
            'physical': 0.25,
            'technical': 0.20,
            'tactical': 0.15,
            'psychological': 0.15
        }
        
        # Score base inicial
        base_score = (
            biotype_score * weights['biotype'] +
            physical_score * weights['physical'] +
            tech_score * weights['technical'] +
            tactic_score * weights['tactical'] +
            psych_score * weights['psychological']
        )
        
        # Ajustes específicos por esporte
        sport_name_lower = sport_name.lower()
        
        # Altura para basquete e vôlei
        if user_data['biotipo']['altura'] >= 180 and any(s in sport_name_lower for s in ['basketball', 'volleyball']):
            base_score *= 1.15
            
        # Força para esportes de força
        if any(s in sport_name_lower for s in ['weightlifting', 'wrestling', 'boxing']):
            strength = user_data['dados_fisicos'].get('forca_superior', 0)
            if strength >= 40:
                base_score *= 1.1
                
        # Velocidade para esportes de velocidade
        if any(s in sport_name_lower for s in ['athletics', 'swimming', 'cycling']):
            speed = user_data['dados_fisicos'].get('velocidade', 5.0)
            if speed <= 3.5:
                base_score *= 1.1
                
        # Equilíbrio para ginástica
        if 'gymnastics' in sport_name_lower:
            balance = user_data['habilidades_tecnicas'].get('equilibrio', 0)
            if balance >= 50:
                base_score *= 1.1
        
        # Fator de idade
        age_factor = min(1.0, max(0.6, (user_data['idade'] - 10) / 8))
        base_score *= age_factor
        
        # Limitar score final
return min(100, max(20, base_score))

    except Exception as e:
        st.warning(f"Erro no cálculo do score base: {str(e)}")
        return 50.0
            
    # Imprimir recomendações
    print("Recomendações de Esportes:")
    for rec in recomendacoes:
        print(f"\nEsporte: {rec['name']}")
        print(f"Compatibilidade: {rec['compatibility']}%")
        print("Pontos Fortes:", rec['strengths'])
        print("Áreas de Desenvolvimento:", rec['development'])
