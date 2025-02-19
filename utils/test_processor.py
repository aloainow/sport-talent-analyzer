# utils/test_processor.py

def process_test_results(test_data):
    """
    Processa os resultados dos testes e retorna os dados normalizados
    """
    results = {}
    
    # Processamento dos resultados de força
    if 'força' in test_data:
        força_results = test_data['força']
        results['physical'] = {
            'flexoes': normalize_score(força_results.get('flexoes', 0), 0, 50),
            'abdominais': normalize_score(força_results.get('abdominais', 0), 0, 50),
            'average': calculate_average([
                normalize_score(força_results.get('flexoes', 0), 0, 50),
                normalize_score(força_results.get('abdominais', 0), 0, 50)
            ])
        }
    
    # Adicione processamento para outros tipos de testes aqui
    
    return results

def normalize_score(value, min_val, max_val):
    """
    Normaliza um valor entre 0 e 10
    """
    if max_val == min_val:
        return 0
    normalized = ((value - min_val) / (max_val - min_val)) * 10
    return max(0, min(10, normalized))

def calculate_average(scores):
    """
    Calcula a média de uma lista de scores
    """
    if not scores:
        return 0
    return sum(scores) / len(scores)
