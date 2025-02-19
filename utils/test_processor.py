# utils/test_processor.py

import numpy as np

def normalize_score(value, min_val, max_val, inverse=False):
    """Normaliza um valor para escala 0-100"""
    if inverse:
        return max(0, min(100, ((max_val - value) / (max_val - min_val)) * 100))
    return max(0, min(100, ((value - min_val) / (max_val - min_val)) * 100))

def calculate_average(values):
    """Calcula a média de uma lista de valores, ignorando None"""
    valid_values = [v for v in values if v is not None]
    return np.mean(valid_values) if valid_values else 0

def process_test_results(results):
    """Processa os resultados dos testes e retorna scores normalizados"""
    scores = {
        'dados_fisicos': 0,
        'habilidades_tecnicas': 0,
        'aspectos_taticos': 0,
        'fatores_psicologicos': 0
    }
    
    # Processamento dos dados físicos
    if 'dados_fisicos' in results:
        df = results['dados_fisicos']
        velocidade_score = normalize_score(df.get('velocidade', 4.0), 4.0, 3.0)
        forca_sup_score = normalize_score(df.get('forca_superior', 0), 10, 26)
        forca_inf_score = normalize_score(df.get('forca_inferior', 0), 20, 41)
        scores['dados_fisicos'] = calculate_average([velocidade_score, forca_sup_score, forca_inf_score])

    # Processamento das habilidades técnicas
    if 'habilidades_tecnicas' in results:
        ht = results['habilidades_tecnicas']
        coord_score = normalize_score(ht.get('coordenacao', 0), 0, 30)
        prec_score = normalize_score(ht.get('precisao', 0), 0, 10)
        agil_score = normalize_score(ht.get('agilidade', 12), 12, 8, inverse=True)
        equil_score = normalize_score(ht.get('equilibrio', 0), 0, 40)
        scores['habilidades_tecnicas'] = calculate_average([coord_score, prec_score, agil_score, equil_score])

    # Processamento dos aspectos táticos
    if 'aspectos_taticos' in results:
        at = results['aspectos_taticos']
        decisao_score = normalize_score(at.get('tomada_decisao', 0), 0, 10)
        visao_score = normalize_score(at.get('visao_jogo', 0), 0, 10)
        posic_score = normalize_score(at.get('posicionamento', 0), 0, 10)
        scores['aspectos_taticos'] = calculate_average([decisao_score, visao_score, posic_score])

    # Processamento dos fatores psicológicos
    if 'fatores_psicologicos' in results:
        fp = results['fatores_psicologicos']
        
        motivacao = calculate_average([
            fp.get('motivacao', {}).get('dedicacao', 5),
            fp.get('motivacao', {}).get('frequencia', 5),
            fp.get('motivacao', {}).get('comprometimento', 5)
        ])
        
        resiliencia = calculate_average([
            fp.get('resiliencia', {}).get('derrotas', 5),
            fp.get('resiliencia', {}).get('criticas', 5),
            fp.get('resiliencia', {}).get('erros', 5)
        ])
        
        trabalho_equipe = calculate_average([
            fp.get('trabalho_equipe', {}).get('comunicacao', 5),
            fp.get('trabalho_equipe', {}).get('opinioes', 5),
            fp.get('trabalho_equipe', {}).get('contribuicao', 5)
        ])
        
        scores['fatores_psicologicos'] = calculate_average([motivacao, resiliencia, trabalho_equipe]) * 10

    return scores
