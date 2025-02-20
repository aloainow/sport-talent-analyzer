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
        if not test_results:
            return {
                'dados_fisicos': 0,
                'habilidades_tecnicas': 0,
                'aspectos_taticos': 0,
                'fatores_psicologicos': 0
            }

        # Processar dados físicos
        dados_fisicos = test_results.get('dados_fisicos', {})
        if dados_fisicos:
            velocidade_score = normalize_score(dados_fisicos.get('velocidade'), 2.5, 5.0, inverse=True)
            forca_sup_score = normalize_score(dados_fisicos.get('forca_superior'), 0, 50)
            forca_inf_score = normalize_score(dados_fisicos.get('forca_inferior'), 0, 60)
            score_fisico = calculate_average([velocidade_score, forca_sup_score, forca_inf_score])
        else:
            score_fisico = 0

        # Processar habilidades técnicas
        habilidades_tecnicas = test_results.get('habilidades_tecnicas', {})
        if habilidades_tecnicas:
            coord_score = normalize_score(habilidades_tecnicas.get('coordenacao'), 0, 50)
            prec_score = normalize_score(habilidades_tecnicas.get('precisao'), 0, 10)
            agil_score = normalize_score(habilidades_tecnicas.get('agilidade'), 5, 15, inverse=True)
            equil_score = normalize_score(habilidades_tecnicas.get('equilibrio'), 0, 60)
            score_tecnico = calculate_average([coord_score, prec_score, agil_score, equil_score])
        else:
            score_tecnico = 0

        # Processar aspectos táticos
        aspectos_taticos = test_results.get('aspectos_taticos', {})
        if aspectos_taticos:
            decisao_score = normalize_score(aspectos_taticos.get('tomada_decisao'), 0, 10)
            visao_score = normalize_score(aspectos_taticos.get('visao_jogo'), 0, 10)
            posic_score = normalize_score(aspectos_taticos.get('posicionamento'), 1, 10)
            score_tatico = calculate_average([decisao_score, visao_score, posic_score])
        else:
            score_tatico = 0

        # Processar fatores psicológicos
        fatores_psicologicos = test_results.get('fatores_psicologicos', {})
        if fatores_psicologicos:
            # Motivação
            mot = fatores_psicologicos.get('motivacao', {})
            motivacao = calculate_average([
                mot.get('dedicacao'),
                mot.get('frequencia'),
                mot.get('comprometimento')
            ])
            
            # Resiliência
            res = fatores_psicologicos.get('resiliencia', {})
            resiliencia = calculate_average([
                res.get('derrotas'),
                res.get('criticas'),
                res.get('erros')
            ])
            
            # Trabalho em equipe
            eq = fatores_psicologicos.get('trabalho_equipe', {})
            trabalho_equipe = calculate_average([
                eq.get('comunicacao'),
                eq.get('opinioes'),
                eq.get('contribuicao')
            ])
            
            score_psicologico = calculate_average([
                normalize_score(motivacao, 0, 10),
                normalize_score(resiliencia, 0, 10),
                normalize_score(trabalho_equipe, 0, 10)
            ])
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
                return {
            'dados_fisicos': 0,
            'habilidades_tecnicas': 0,
            'aspectos_taticos': 0,
            'fatores_psicologicos': 0
        }

def normalize_olympic_stats(value, mean, min_val, max_val):
    """
    Normaliza um valor em relação às estatísticas olímpicas
    
    Args:
        value: Valor a ser normalizado
        mean: Média olímpica
        min_val: Valor mínimo olímpico
        max_val: Valor máximo olímpico
    
    Returns:
        float: Score normalizado de 0 a 100
    """
    try:
        if value is None:
            return 0
            
        value = float(value)
        
        # Se o valor está dentro do range olímpico
        if min_val <= value <= max_val:
            # Quanto mais próximo da média, melhor o score
            deviation = abs(value - mean)
            max_deviation = max(mean - min_val, max_val - mean)
            return 100 * (1 - deviation / max_deviation)
        
        # Se está fora do range, penaliza proporcionalmente
        if value < min_val:
            return max(0, 50 * (value / min_val))
        else:
            return max(0, 50 * (max_val / value))
            
    except (TypeError, ValueError):
        return 0

def get_attribute_importance(attribute_name: str) -> float:
    """
    Retorna o peso de importância para cada atributo na comparação
    
    Args:
        attribute_name: Nome do atributo
        
    Returns:
        float: Peso do atributo (0 a 1)
    """
    importance_weights = {
        'altura': 0.3,
        'peso': 0.3,
        'velocidade': 0.4,
        'forca_superior': 0.3,
        'forca_inferior': 0.3,
        'coordenacao': 0.25,
        'precisao': 0.25,
        'agilidade': 0.25,
        'equilibrio': 0.25,
        'tomada_decisao': 0.2,
        'visao_jogo': 0.2,
        'posicionamento': 0.2
    }
    
    return importance_weights.get(attribute_name, 0.1)  # default 0.1 para outros atributos
