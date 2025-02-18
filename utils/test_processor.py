def process_test_results(test_results):
    """
    Processa os resultados dos testes e calcula médias e scores normalizados.
    """
    processed_results = {
        'physical': {},
        'technical': {},
        'tactical': {},
        'psychological': {}
    }

    # Processamento dos testes físicos
    if test_results.get('physical'):
        physical = test_results['physical']
        processed_results['physical'] = {
            'velocity': normalize_score(physical.get('velocity', 0), 'velocity'),
            'strength': normalize_score(physical.get('strength', 0), 'strength'),
            'endurance': normalize_score(physical.get('endurance', 0), 'endurance'),
            'agility': normalize_score(physical.get('agility', 0), 'agility'),
            'average': calculate_average(physical)
        }

    # Processamento dos testes técnicos
    if test_results.get('technical'):
        technical = test_results['technical']
        processed_results['technical'] = {
            'coordination': normalize_score(technical.get('coordination', 0), 'coordination'),
            'balance': normalize_score(technical.get('balance', 0), 'balance'),
            'precision': normalize_score(technical.get('precision', 0), 'precision'),
            'average': calculate_average(technical)
        }

    # Processamento dos testes táticos
    if test_results.get('tactical'):
        tactical = test_results['tactical']
        processed_results['tactical'] = {
            'decision_making': tactical.get('decision_making', 0),
            'game_vision': tactical.get('game_vision', 0),
            'average': calculate_average(tactical)
        }

    # Processamento dos testes psicológicos (já estão em escala 1-10)
    if test_results.get('psychological'):
        psychological = test_results['psychological']
        processed_results['psychological'] = {
            'motivation': psychological.get('motivation', 0),
            'teamwork': psychological.get('teamwork', 0),
            'leadership': psychological.get('leadership', 0),
            'resilience': psychological.get('resilience', 0),
            'concentration': psychological.get('concentration', 0),
            'competitiveness': psychological.get('competitiveness', 0),
            'average': calculate_average(psychological)
        }

    return processed_results

def normalize_score(value, test_type):
    """
    Normaliza os scores para uma escala de 0-10.
    """
    # Definição dos valores de referência para cada tipo de teste
    reference_values = {
        'velocity': {'min': 15, 'max': 5},  # segundos (invertido)
        'strength': {'min': 0, 'max': 50},  # repetições
        'endurance': {'min': 0, 'max': 3000},  # metros
        'agility': {'min': 20, 'max': 10},  # segundos (invertido)
        'coordination': {'min': 0, 'max': 10},
        'balance': {'min': 0, 'max': 60},  # segundos
        'precision': {'min': 0, 'max': 10}
    }

    if test_type not in reference_values:
        return value

    ref = reference_values[test_type]
    
    # Para testes onde menor valor é melhor (como velocidade)
    if test_type in ['velocity', 'agility']:
        if value <= ref['max']:
            return 10
        elif value >= ref['min']:
            return 0
        return 10 * (ref['min'] - value) / (ref['min'] - ref['max'])
    
    # Para testes onde maior valor é melhor
    else:
        if value >= ref['max']:
            return 10
        elif value <= ref['min']:
            return 0
        return 10 * (value - ref['min']) / (ref['max'] - ref['min'])

def calculate_average(results):
    """
    Calcula a média dos resultados
