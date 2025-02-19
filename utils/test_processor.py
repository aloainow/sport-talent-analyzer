import numpy as np

def normalize_score(value, min_val, max_val, inverse=False):
    """Normaliza um valor para escala 0-100"""
    try:
        if value is None:
            return 0
        value = float(value)
        if inverse:
            # Para métricas onde menor valor é melhor (ex: tempo)
            if value <= min_val:
                return 100
            elif value >= max_val:
                return 0
            return ((max_val - value) / (max_val - min_val)) * 100
        else:
            # Para métricas onde maior valor é melhor
            if value >= max_val:
                return 100
            elif value <= min_val:
                return 0
            return ((value - min_val) / (max_val - min_val)) * 100
    except (TypeError, ValueError):
        return 0

def calculate_average(values):
    """Calcula a média de uma lista de valores, ignorando None"""
    valid_values = [v for v in values if v is not None and isinstance(v, (int, float))]
    if not valid_values:
        return 0
    return float(np.mean(valid_values))

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
        # Velocidade: 3.0s (excelente) a 4.5s (fraco)
        velocidade_score = normalize_score(df.get('velocidade'), 4.5, 3.0, inverse=True)
        # Força superior: 5 (fraco) a 30 (excelente) repetições
        forca_sup_score = normalize_score(df.get('forca_superior'), 5, 30)
        # Força inferior: 15 (fraco) a 45 (excelente) repetições
        forca_inf_score = normalize_score(df.get('forca_inferior'), 15, 45)
        
        scores['dados_fisicos'] = calculate_average([
            velocidade_score,
            forca_sup_score,
            forca_inf_score
        ])

    # Processamento das habilidades técnicas
    if 'habilidades_tecnicas' in results:
        ht = results['habilidades_tecnicas']
        # Coordenação: 10 (fraco) a 40 (excelente) alternâncias
        coord_score = normalize_score(ht.get('coordenacao'), 10, 40)
        # Precisão: 0 (fraco) a 10 (excelente) acertos
        prec_score = normalize_score(ht.get('precisao'), 0, 10)
        # Agilidade: 14s (fraco) a 8s (excelente)
        agil_score = normalize_score(ht.get('agilidade'), 14, 8, inverse=True)
        # Equilíbrio: 10s (fraco) a 60s (excelente)
        equil_score = normalize_score(ht.get('equilibrio'), 10, 60)
        
        scores['habilidades_tecnicas'] = calculate_average([
            coord_score,
            prec_score * 10,  # Ajuste para escala 0-100
            agil_score,
            equil_score
        ])

    # Processamento dos aspectos táticos
    if 'aspectos_taticos' in results:
        at = results['aspectos_taticos']
        # Todos os scores táticos são de 1-10
        decisao_score = normalize_score(at.get('tomada_decisao'), 1, 10)
        visao_score = normalize_score(at.get('visao_jogo'), 1, 10)
        posic_score = normalize_score(at.get('posicionamento'), 1, 10)
        
        scores['aspectos_taticos'] = calculate_average([
            decisao_score * 10,  # Ajuste para escala 0-100
            visao_score * 10,
            posic_score * 10
        ])

    # Processamento dos fatores psicológicos
    if 'fatores_psicologicos' in results:
        fp = results['fatores_psicologicos']
        
        motivacao = calculate_average([
            normalize_score(fp.get('motivacao', {}).get('dedicacao'), 1, 10),
            normalize_score(fp.get('motivacao', {}).get('frequencia'), 1, 10),
            normalize_score(fp.get('motivacao', {}).get('comprometimento'), 1, 10)
        ])
        
        resiliencia = calculate_average([
            normalize_score(fp.get('resiliencia', {}).get('derrotas'), 1, 10),
            normalize_score(fp.get('resiliencia', {}).get('criticas'), 1, 10),
            normalize_score(fp.get('resiliencia', {}).get('erros'), 1, 10)
        ])
        
        trabalho_equipe = calculate_average([
            normalize_score(fp.get('trabalho_equipe', {}).get('comunicacao'), 1, 10),
            normalize_score(fp.get('trabalho_equipe', {}).get('opinioes'), 1, 10),
            normalize_score(fp.get('trabalho_equipe', {}).get('contribuicao'), 1, 10)
        ])
        
        scores['fatores_psicologicos'] = calculate_average([
            motivacao * 10,  # Ajuste para escala 0-100
            resiliencia * 10,
            trabalho_equipe * 10
        ])

    return scores
