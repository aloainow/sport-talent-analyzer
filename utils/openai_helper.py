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
def load_and_process_data() -> pd.DataFrame:
    """
    Carrega e processa os dados dos esportes olímpicos do CSV
    """
    try:
        # Lista de possíveis caminhos para o arquivo CSV
        possible_paths = [
            'data/perfil_eventos_olimpicos_verao.csv',  # Caminho padrão no Streamlit Cloud
            './data/perfil_eventos_olimpicos_verao.csv',
            os.path.join('data', 'perfil_eventos_olimpicos_verao.csv'),
            './perfil_eventos_olimpicos_verao.csv',
            'perfil_eventos_olimpicos_verao.csv'
        ]
        
        # Tenta carregar o arquivo de diferentes locais
        for path in possible_paths:
            try:
                if os.path.exists(path):
                    print(f"📁 Carregando arquivo CSV de: {path}")
                    df = pd.read_csv(path)
                    
                    # Verifica se o DataFrame não está vazio
                    if not df.empty:
                        return df
            except Exception as inner_e:
                print(f"Erro ao tentar carregar {path}: {inner_e}")
        
        # Se nenhum arquivo for encontrado, usa dados padrão
        st.warning("⚠️ CSV não encontrado. Usando dados padrão.")
        return pd.DataFrame(data_sports_default())
    
    except Exception as e:
        st.error(f"Erro ao carregar dados dos esportes: {str(e)}")
        return pd.DataFrame(data_sports_default())

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

def get_sport_recommendations(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Gera recomendações de esportes baseadas nos dados do usuário
    """
    try:
        # Verificações de entrada
        if not user_data or not all(user_data.get(key) for key in ['dados_fisicos', 'habilidades_tecnicas', 'aspectos_taticos', 'fatores_psicologicos']):
            st.error("Por favor, complete todos os testes antes de gerar recomendações.")
            return []

        # Carregar dados dos esportes
        sports_data = load_and_process_data()
        if sports_data is None:
            st.warning("Falha ao carregar dados. Exibindo sugestões padrão.")
            return get_recommendations_without_api(user_data.get('genero', 'Masculino'))

        # Definir gênero do usuário - Pegar do personal_info
        user_gender = st.session_state.personal_info.get('genero', 'Masculino')
        user_age = st.session_state.personal_info.get('idade', 18)

        # Filtrar esportes por gênero de forma mais precisa
        if user_gender == "Feminino":
            sports_data = sports_data[sports_data['Event'].str.contains("Women's", case=False, na=False)]
        else:  # Masculino
            sports_data = sports_data[sports_data['Event'].str.contains("Men's", case=False, na=False)]

        if sports_data.empty:
            st.warning(f"Nenhum esporte encontrado para o gênero {user_gender}")
            return get_recommendations_without_api(user_gender)

        recommendations = []

        for _, sport in sports_data.iterrows():
            try:
                sport_name = sport['Event']
                
                # Calcular scores individuais
                biotype_score = calculate_biotype_compatibility(user_data, sport)
                physical_score = calculate_physical_compatibility(user_data, sport_name, user_age)

                # Calcular scores técnicos e táticos
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

                # Calcular score psicológico
                psychological_scores = []
                if user_data.get('fatores_psicologicos'):
                    psych_data = user_data['fatores_psicologicos']
                    
                    # Motivação
                    if 'motivacao' in psych_data:
                        mot_score = np.mean([
                            psych_data['motivacao'].get('dedicacao', 5),
                            psych_data['motivacao'].get('frequencia', 5),
                            psych_data['motivacao'].get('comprometimento', 5)
                        ])
                        psychological_scores.append(normalize_score(mot_score, 0, 10))
                    
                    # Resiliência
                    if 'resiliencia' in psych_data:
                        res_score = np.mean([
                            psych_data['resiliencia'].get('derrotas', 5),
                            psych_data['resiliencia'].get('criticas', 5),
                            psych_data['resiliencia'].get('erros', 5)
                        ])
                        psychological_scores.append(normalize_score(res_score, 0, 10))
                    
                    # Trabalho em equipe
                    if 'trabalho_equipe' in psych_data:
                        team_score = np.mean([
                            psych_data['trabalho_equipe'].get('comunicacao', 5),
                            psych_data['trabalho_equipe'].get('opinioes', 5),
                            psych_data['trabalho_equipe'].get('contribuicao', 5)
                        ])
                        psychological_scores.append(normalize_score(team_score, 0, 10))

                psych_score = np.mean(psychological_scores) if psychological_scores else 50

                # Calcular score base com os pesos atualizados
                base_score = (
                    biotype_score * 0.25 +  # Reduzido de 0.30
                    physical_score * 0.25 +  # Mantido
                    tech_score * 0.20 +      # Reduzido de 0.25
                    tactic_score * 0.15 +    # Reduzido de 0.20
                    psych_score * 0.15       # Novo componente
                ) * 0.7

                # Ajustes específicos por esporte
                sport_name_lower = sport_name.lower()
                
                # Ajustes para esportes que valorizam altura
                if user_data.get('biotipo', {}).get('altura', 0) >= 180 and any(s in sport_name_lower for s in ['basketball', 'volleyball']):
                    base_score *= 1.1
                
                # Ajustes para esportes que valorizam força
                if any(s in sport_name_lower for s in ['weightlifting', 'wrestling', 'boxing']):
                    strength_bonus = (user_data.get('dados_fisicos', {}).get('forca_superior', 0) / 50.0) * 0.1
                    base_score *= (1 + strength_bonus)
                
                # Ajustes para esportes que valorizam velocidade
                if any(s in sport_name_lower for s in ['athletics', 'swimming', 'cycling']):
                    speed = user_data.get('dados_fisicos', {}).get('velocidade', 5.0)
                    if speed < 4.0:  # Velocidade boa
                        base_score *= 1.1
                
                # Ajustes para esportes técnicos
                if any(s in sport_name_lower for s in ['gymnastics', 'diving', 'figure skating']):
                    tech_bonus = (tech_score / 100.0) * 0.15
                    base_score *= (1 + tech_bonus)

                # Fator de idade
                age_factor = min(1.0, max(0.6, (user_age - 10) / 8))

                # Variação aleatória leve para evitar resultados idênticos
                random_factor = np.random.uniform(0.95, 1.05)
                
                # Calcular score final
                final_score = min(100, max(20, base_score * age_factor * random_factor))

                # Traduzir nome do esporte
                translated_name = translate_sport_name(sport_name, user_gender)

                # Adicionar à lista de recomendações
                recommendations.append({
                    "name": translated_name,
                    "compatibility": round(final_score),
                    "strengths": get_sport_strengths(sport_name, user_data),
                    "development": get_development_areas(sport_name, user_data),
                    "scores": {
                        "biotype": round(biotype_score),
                        "physical": round(physical_score),
                        "technical": round(tech_score),
                        "tactical": round(tactic_score),
                        "psychological": round(psych_score)
                    }
                })

            except Exception as sport_e:
                st.warning(f"Erro ao processar esporte {sport_name}: {str(sport_e)}")
                continue

        # Ordenar recomendações por compatibilidade
        recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
        
        # Retornar top 10 recomendações
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

# Código de exemplo para teste/verificação
if __name__ == '__main__':
    # Exemplo de dados de usuário para teste
    exemplo_dados_usuario = {
        'genero': 'Masculino',
        'idade': 16,
        'biotipo': {
            'altura': 175,
            'peso': 70,
            'envergadura': 180
        },
        'dados_fisicos': {
            'velocidade': 4.0,
            'forca_superior': 35,
            'forca_inferior': 45
        },
        'habilidades_tecnicas': {
            'coordenacao': 40,
            'precisao': 7,
            'agilidade': 8,
            'equilibrio': 45
        },
        'aspectos_taticos': {
            'tomada_decisao': 7,
            'visao_jogo': 6,
            'posicionamento': 7
        },
        'fatores_psicologicos': {
            'motivacao': {
                'dedicacao': 8,
                'frequencia': 7,
                'comprometimento': 8
            },
            'resiliencia': {
                'derrotas': 7,
                'criticas': 6,
                'erros': 7
            },
            'trabalho_equipe': {
                'comunicacao': 8,
                'opinioes': 7,
                'contribuicao': 8
            }
        }
    }
    
    # Gerar recomendações
    recomendacoes = get_sport_recommendations(exemplo_dados_usuario)
    
    # Imprimir recomendações
    print("Recomendações de Esportes:")
    for rec in recomendacoes:
        print(f"\nEsporte: {rec['name']}")
        print(f"Compatibilidade: {rec['compatibility']}%")
        print("Pontos Fortes:", rec['strengths'])
        print("Áreas de Desenvolvimento:", rec['development'])
