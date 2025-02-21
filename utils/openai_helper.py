import pandas as pd
import json
import numpy as np
from typing import Dict, List, Any
import os
import streamlit as st

import pandas as pd
import json
import numpy as np
from typing import Dict, List, Any
import os
import streamlit as st

def normalize_score(value, min_val, max_val, inverse=False):
    """Normaliza um valor para escala 0-100"""
    try:
        if value is None or value == "":  # Adicionado para evitar NoneType
            return 0
        value = float(value)
        if inverse:
            if value <= min_val:
                return 100
            elif value >= max_val:
                return 0
            return ((max_val - value) / (max_val - min_val)) * 100
        else:
            if value <= min_val:
                return 0
            elif value >= max_val:
                return 100
            return ((value - min_val) / (max_val - min_val)) * 100
    except Exception as e:
        return 0

# Outras funções corrigidas abaixo...

try:
    # Bloco de código principal que pode gerar erro
    scores = []
    # Velocidade (esportes que valorizam velocidade)
    # Força (esportes que valorizam força)
    # Calcular média dos scores disponíveis
    base_score = np.mean(scores)
    # Ajuste baseado na idade
except Exception as e:
    st.error(f"Erro ao calcular média dos scores: {str(e)}")

try:
    biotype_data = user_data['biotipo']
    # Altura (150-220 cm)
    # Esportes que valorizam altura
    # Peso (40-120 kg)
    # Categorias de peso para esportes de combate
except Exception as e:
    st.error(f"Erro ao processar biotipo: {str(e)}")
        
def classify_test_results(test_name: str, value: float, gender: str) -> str:
    """Classifica o resultado do teste com base no gênero"""
    classification_criteria = {
        "push_ups": {
            "Masculino": [(0, 20, "Iniciante"), (21, 40, "Intermediário"), (41, float('inf'), "Avançado")],
            "Feminino": [(0, 10, "Iniciante"), (11, 30, "Intermediário"), (31, float('inf'), "Avançado")]
        },
        "sit_ups": {
            "Masculino": [(0, 25, "Iniciante"), (26, 50, "Intermediário"), (51, float('inf'), "Avançado")],
            "Feminino": [(0, 15, "Iniciante"), (16, 40, "Intermediário"), (41, float('inf'), "Avançado")]
        }
    }
    
    if test_name in classification_criteria and gender in classification_criteria[test_name]:
        for lower, upper, label in classification_criteria[test_name][gender]:
            if lower <= value <= upper:
                return label
    return "Não classificado"
    
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

def calculate_biotype_compatibility(user_data: Dict, sport: pd.Series, user_gender: str) -> float:
    """Cálculo melhorado de compatibilidade biotipo"""
    try:
        # Pegar dados do CSV de perfil olímpico
        sport_name = sport['Event'].lower()
        altura = st.session_state.personal_info.get('altura', 170)
        peso = st.session_state.personal_info.get('peso', 60)
        
        scores = []
        
        # Comparar com médias olímpicas (usando os dados do CSV)
        if 'basketball' in sport_name:
            altura_score = normalize_score(altura, 170, 200)
            scores.append(altura_score * 1.5)  # Peso maior para altura no basquete
        elif 'volleyball' in sport_name:
            altura_score = normalize_score(altura, 165, 195)
            scores.append(altura_score * 1.3)
        elif 'gymnastics' in sport_name:
            altura_score = normalize_score(altura, 145, 170)
            peso_score = normalize_score(peso, 40, 65)
            scores.extend([altura_score, peso_score])
        
        # Score padrão se não houver regras específicas
        if not scores:
            scores.append(70)  # Score base razoável
            
        return np.mean(scores)
    except Exception as e:
        print(f"Erro no cálculo de biotipo: {str(e)}")
        return 50

def calculate_physical_compatibility(user_data: Dict, sport_name: str, user_age: int) -> float:
    """Cálculo melhorado de compatibilidade física"""
    try:
        if not user_data.get('dados_fisicos'):
            return 50
            
        sport_name = sport_name.lower()
        dados_fisicos = user_data['dados_fisicos']
        
        scores = []
        
        # Velocidade
        if any(s in sport_name for s in ['athletics', 'swimming', 'basketball']):
            vel_score = normalize_score(dados_fisicos.get('velocidade', 5), 2.5, 5.0, inverse=True)
            scores.append(vel_score * 1.3)
        
        # Força Superior
        if any(s in sport_name for s in ['gymnastics', 'wrestling', 'volleyball']):
            forca_sup = normalize_score(dados_fisicos.get('forca_superior', 0), 0, 50)
            scores.append(forca_sup * 1.2)
        
        # Força Inferior
        if any(s in sport_name for s in ['athletics', 'football', 'basketball']):
            forca_inf = normalize_score(dados_fisicos.get('forca_inferior', 0), 0, 60)
            scores.append(forca_inf * 1.2)
        
        if not scores:
            return 60  # Score base para esportes sem requisitos específicos
            
        base_score = np.mean(scores)
        
        # Ajuste por idade mais suave
        age_factor = min(1.0, max(0.8, (user_age - 10) / 8))
        
        return base_score * age_factor
    except Exception as e:
        print(f"Erro no cálculo físico: {str(e)}")
        return 50

def get_sport_strengths(sport_name: str, user_data: Dict) -> List[str]:
    """Identificação melhorada de pontos fortes"""
    strengths = []
    sport_name = sport_name.lower()
    
    try:
        # Dados Físicos
        if user_data.get('dados_fisicos'):
            dados_fisicos = user_data['dados_fisicos']
            
            if dados_fisicos.get('velocidade', 6) < 4.0:
                strengths.append("Velocidade excepcional")
            elif dados_fisicos.get('velocidade', 6) < 4.5:
                strengths.append("Boa velocidade")
                
            if dados_fisicos.get('forca_superior', 0) > 35:
                strengths.append("Força superior excepcional")
            elif dados_fisicos.get('forca_superior', 0) > 25:
                strengths.append("Boa força superior")
                
            if dados_fisicos.get('forca_inferior', 0) > 45:
                strengths.append("Força inferior excepcional")
            elif dados_fisicos.get('forca_inferior', 0) > 35:
                strengths.append("Boa força inferior")
        
        # Habilidades Técnicas
        if user_data.get('habilidades_tecnicas'):
            hab_tec = user_data['habilidades_tecnicas']
            
            if hab_tec.get('coordenacao', 0) > 35:
                strengths.append("Coordenação motora excepcional")
            elif hab_tec.get('coordenacao', 0) > 25:
                strengths.append("Boa coordenação motora")
                
            if hab_tec.get('precisao', 0) > 7:
                strengths.append("Alta precisão")
            if hab_tec.get('equilibrio', 0) > 45:
                strengths.append("Equilíbrio excepcional")
            if hab_tec.get('agilidade', 0) < 11:
                strengths.append("Agilidade destacada")
        
        # Aspectos Táticos
        if user_data.get('aspectos_taticos'):
            taticos = user_data['aspectos_taticos']
            
            if taticos.get('tomada_decisao', 0) > 7:
                strengths.append("Excelente tomada de decisão")
            if taticos.get('visao_jogo', 0) > 7:
                strengths.append("Ótima visão de jogo")
            if taticos.get('posicionamento', 0) > 7:
                strengths.append("Posicionamento inteligente")
        
        # Retorna apenas os pontos fortes mais relevantes para o esporte
        relevant_strengths = []
        if 'basketball' in sport_name:
            keywords = ['altura', 'agilidade', 'coordenação', 'visão']
        elif 'volleyball' in sport_name:
            keywords = ['altura', 'força', 'precisão', 'posicionamento']
        elif 'athletics' in sport_name:
            keywords = ['velocidade', 'força', 'agilidade']
        else:
            keywords = []
            
        for strength in strengths:
            if any(keyword.lower() in strength.lower() for keyword in keywords):
                relevant_strengths.append(strength)
                
        # Se não encontrou pontos fortes específicos, usa os melhores gerais
        if not relevant_strengths:
            relevant_strengths = sorted(strengths, key=len)[:3]
            
        return relevant_strengths[:3] if relevant_strengths else ["Avaliação pendente"]
        
    except Exception as e:
        print(f"Erro ao identificar pontos fortes: {str(e)}")
        return ["Avaliação pendente"]
def calculate_sport_compatibility(user_data: Dict, sport: Dict) -> float:
    """
    Calcula a compatibilidade específica para cada esporte
    """
    scores = []
    
    # Dados físicos (peso 30%)
    if user_data.get('dados_fisicos'):
        velocidade_score = normalize_score(
            user_data['dados_fisicos'].get('velocidade', 5),
            2.5, 5.0, inverse=True
        )
        forca_sup_score = normalize_score(
            user_data['dados_fisicos'].get('forca_superior', 0),
            0, 50
        )
        forca_inf_score = normalize_score(
            user_data['dados_fisicos'].get('forca_inferior', 0),
            0, 60
        )
        scores.append(np.mean([velocidade_score, forca_sup_score, forca_inf_score]) * 0.3)
    
    # Habilidades técnicas (peso 30%)
    if user_data.get('habilidades_tecnicas'):
        coord_score = normalize_score(
            user_data['habilidades_tecnicas'].get('coordenacao', 0),
            0, 50
        )
        prec_score = normalize_score(
            user_data['habilidades_tecnicas'].get('precisao', 0),
            0, 10
        )
        agil_score = normalize_score(
            user_data['habilidades_tecnicas'].get('agilidade', 15),
            5, 15, inverse=True
        )
        equil_score = normalize_score(
            user_data['habilidades_tecnicas'].get('equilibrio', 0),
            0, 60
        )
        scores.append(np.mean([coord_score, prec_score, agil_score, equil_score]) * 0.3)
    
    # Aspectos táticos (peso 20%)
    if user_data.get('aspectos_taticos'):
        taticos = user_data['aspectos_taticos']
        decisao_score = normalize_score(taticos.get('tomada_decisao', 0), 0, 10)
        visao_score = normalize_score(taticos.get('visao_jogo', 0), 0, 10)
        posic_score = normalize_score(taticos.get('posicionamento', 0), 0, 10)
        scores.append(np.mean([decisao_score, visao_score, posic_score]) * 0.2)
    
    # Fatores psicológicos (peso 20%)
    if user_data.get('fatores_psicologicos'):
        psic = user_data['fatores_psicologicos']
        mot_scores = [
            psic.get('motivacao', {}).get(k, 0)
            for k in ['dedicacao', 'frequencia', 'comprometimento']
        ]
        res_scores = [
            psic.get('resiliencia', {}).get(k, 0)
            for k in ['derrotas', 'criticas', 'erros']
        ]
        team_scores = [
            psic.get('trabalho_equipe', {}).get(k, 0)
            for k in ['comunicacao', 'opinioes', 'contribuicao']
        ]
        
        psic_score = np.mean([
            np.mean(mot_scores),
            np.mean(res_scores),
            np.mean(team_scores)
        ])
        scores.append(normalize_score(psic_score, 0, 10) * 0.2)
    
    # Calcula score final
    if not scores:
        return 50.0
        
    base_score = sum(scores)
    
    # Adiciona variação aleatória de ±5%
    variation = np.random.uniform(-5, 5)
    final_score = max(20, min(100, base_score + variation))
    
    return final_score

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
    try:
        if not user_data or not all(user_data.get(key) for key in ['dados_fisicos', 'habilidades_tecnicas', 'aspectos_taticos', 'fatores_psicologicos']):
            st.error("Por favor, complete todos os testes antes de gerar recomendações.")
            return []

        sports_data = load_and_process_data()
        if sports_data is None:
            st.error("Erro ao carregar dados dos esportes. Por favor, tente novamente.")
            return []

        user_gender = st.session_state.personal_info.get('genero', 'Masculino')
        user_age = st.session_state.personal_info.get('idade', 18)

        # Filtragem por gênero
        if user_gender == "Feminino":
            sports_data = sports_data[
                (sports_data['Event'].str.contains("Women", case=False)) |
                (sports_data['Event'].str.contains("Mixed", case=False))
            ]
        else:  # Masculino
            sports_data = sports_data[
                (sports_data['Event'].str.contains("Men", case=False) & 
                ~sports_data['Event'].str.contains("Women", case=False)) |
                (sports_data['Event'].str.contains("Mixed", case=False))
            ]

        if sports_data.empty:
            st.error(f"Não foram encontrados esportes para o gênero {user_gender}.")
            return []

        # Calcular scores dos aspectos com base inicial mais alta
        tech_scores = []
        if user_data.get('habilidades_tecnicas'):
            coord_score = normalize_score(user_data['habilidades_tecnicas'].get('coordenacao', 0), 0, 50) * 1.5
            prec_score = normalize_score(user_data['habilidades_tecnicas'].get('precisao', 0), 0, 10) * 1.4
            agil_score = normalize_score(user_data['habilidades_tecnicas'].get('agilidade', 0), 5, 15, inverse=True) * 1.4
            equil_score = normalize_score(user_data['habilidades_tecnicas'].get('equilibrio', 0), 0, 60) * 1.3
            tech_scores = [coord_score, prec_score, agil_score, equil_score]
        tech_score = np.mean(tech_scores) if tech_scores else 70  # Base score aumentado

        tactic_scores = []
        if user_data.get('aspectos_taticos'):
            decisao_score = normalize_score(user_data['aspectos_taticos'].get('tomada_decisao', 0), 0, 10) * 1.5
            visao_score = normalize_score(user_data['aspectos_taticos'].get('visao_jogo', 0), 0, 10) * 1.4
            posic_score = normalize_score(user_data['aspectos_taticos'].get('posicionamento', 0), 1, 10) * 1.4
            tactic_scores = [decisao_score, visao_score, posic_score]
        tactic_score = np.mean(tactic_scores) if tactic_scores else 70  # Base score aumentado

        recommendations = []
        for _, sport in sports_data.iterrows():
            try:
                sport_name = sport['Event']
                biotype_score = calculate_biotype_compatibility(user_data, sport, user_gender)
                physical_score = calculate_physical_compatibility(user_data, sport_name, user_age)

                # Pesos específicos por esporte
                weights = get_sport_specific_weights(sport_name)
                
                # Cálculo da compatibilidade com base mais alta
                base_score = (
                    biotype_score * weights['biotype'] +
                    physical_score * weights['physical'] +
                    tech_score * weights['technical'] +
                    tactic_score * weights['tactical']
                ) * 1.3  # Multiplicador geral aumentado

                # Variação controlada
                variation = np.random.uniform(-5, 10)  # Mais chance de variação positiva
                final_score = base_score + variation

                # Fator de idade mais favorável
                age_factor = min(1.3, max(0.9, (user_age - 10) / 8))
                final_score = final_score * age_factor

                # Garantir mínimo mais baixo
                final_score = max(30, min(100, final_score))

                translated_name = translate_sport_name(sport_name, user_gender)
                strengths = get_sport_strengths(sport_name, user_data)
                if strengths == ["Avaliação pendente"]:
                    strengths = []

                recommendations.append({
                    "name": translated_name,
                    "compatibility": round(final_score),
                    "strengths": strengths,
                    "development": get_development_areas(sport_name, user_data)
                })

            except Exception as e:
                st.warning(f"Erro ao processar esporte {sport_name}: {str(e)}")
                continue

        # Ordenar por compatibilidade
        recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
        
        # Filtrar com limite mais baixo
        recommendations = [r for r in recommendations if r['compatibility'] > 25]
        
        if not recommendations:
            st.warning("Não foram encontradas recomendações. Tente completar mais testes.")
            return []
        
        return recommendations[:10]

    except Exception as e:
        st.error(f"Erro ao gerar recomendações: {str(e)}")
        return []
        
        def get_sport_specific_weights(sport_name: str) -> Dict[str, float]:
    """
    Retorna pesos específicos para cada aspecto baseado no esporte
    """
    sport_name = sport_name.lower()
    
    # Pesos padrão
    default_weights = {
        'biotype': 0.25,
        'physical': 0.25,
        'technical': 0.25,
        'tactical': 0.25
    }
    
    # Esportes específicos
    if 'basketball' in sport_name:
        return {
            'biotype': 0.3,    # Altura é importante
            'physical': 0.25,
            'technical': 0.25,
            'tactical': 0.2
        }
    elif 'athletics' in sport_name:
        return {
            'biotype': 0.2,
            'physical': 0.4,    # Foco em capacidade física
            'technical': 0.25,
            'tactical': 0.15
        }
    elif 'gymnastics' in sport_name:
        return {
            'biotype': 0.2,
            'physical': 0.3,
            'technical': 0.35,  # Foco em técnica
            'tactical': 0.15
        }
    elif 'volleyball' in sport_name:
        return {
            'biotype': 0.3,
            'physical': 0.2,
            'technical': 0.25,
            'tactical': 0.25
        }
    
    return default_weights
    
