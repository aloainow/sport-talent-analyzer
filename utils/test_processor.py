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

def process_test_results(test_results):
    """
    Processa os resultados dos testes e retorna os scores normalizados.
    """
    try:
        # Verificar se todos os testes foram completados
        if not all(test_results.get(category) for category in ['dados_fisicos', 'habilidades_tecnicas', 'aspectos_taticos', 'fatores_psicologicos']):
            return None

        # Processar dados físicos
        dados_fisicos = test_results.get('dados_fisicos', {})
        if dados_fisicos:
            score_fisico = normalize_score([
                dados_fisicos.get('velocidade', 0),
                dados_fisicos.get('forca_superior', 0),
                dados_fisicos.get('forca_inferior', 0)
            ])
        else:
            score_fisico = 0

        # Processar habilidades técnicas
        habilidades_tecnicas = test_results.get('habilidades_tecnicas', {})
        if habilidades_tecnicas:
            score_tecnico = normalize_score([
                habilidades_tecnicas.get('coordenacao', 0),
                habilidades_tecnicas.get('precisao', 0),
                habilidades_tecnicas.get('agilidade', 0),
                habilidades_tecnicas.get('equilibrio', 0)
            ])
        else:
            score_tecnico = 0

        # Processar aspectos táticos
        aspectos_taticos = test_results.get('aspectos_taticos', {})
        if aspectos_taticos:
            score_tatico = normalize_score([
                aspectos_taticos.get('tomada_decisao', 0),
                aspectos_taticos.get('visao_jogo', 0),
                aspectos_taticos.get('posicionamento', 0)
            ])
        else:
            score_tatico = 0

        # Processar fatores psicológicos
        fatores_psicologicos = test_results.get('fatores_psicologicos', {})
        if fatores_psicologicos:
            motivacao = calculate_average([
                fatores_psicologicos.get('motivacao', {}).get('dedicacao', 0),
                fatores_psicologicos.get('motivacao', {}).get('frequencia', 0),
                fatores_psicologicos.get('motivacao', {}).get('comprometimento', 0)
            ])
            
            resiliencia = calculate_average([
                fatores_psicologicos.get('resiliencia', {}).get('derrotas', 0),
                fatores_psicologicos.get('resiliencia', {}).get('criticas', 0),
                fatores_psicologicos.get('resiliencia', {}).get('erros', 0)
            ])
            
            trabalho_equipe = calculate_average([
                fatores_psicologicos.get('trabalho_equipe', {}).get('comunicacao', 0),
                fatores_psicologicos.get('trabalho_equipe', {}).get('opinioes', 0),
                fatores_psicologicos.get('trabalho_equipe', {}).get('contribuicao', 0)
            ])
            
            score_psicologico = normalize_score([motivacao, resiliencia, trabalho_equipe])
        else:
            score_psicologico = 0

        # Retornar scores processados
        return {
            'dados_fisicos': score_fisico,
            'habilidades_tecnicas': score_tecnico,
            'aspectos_taticos': score_tatico,
            'fatores_psicologicos': score_psicologico
        }
    except Exception as e:
        print(f"Erro no processamento dos scores: {str(e)}")
        return None
