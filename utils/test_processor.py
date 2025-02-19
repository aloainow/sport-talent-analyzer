def process_test_results(results):
    """
    Processa e normaliza os resultados dos testes.
    """
    processed = {
        'força': {},
        'velocidade': {},
        'resistencia': {},
        'coordenacao': {}
    }
    
    # Normalização de força
    if 'força' in results:
        força = results['força']
        processed['força'] = {
            'flexoes': min(10, força.get('flexoes', 0) / 3),  # Max 30 flexões = 10 pontos
            'abdominais': min(10, força.get('abdominais', 0) / 4),  # Max 40 abdominais = 10 pontos
            'average': 0  # Será calculado abaixo
        }
    
    # Normalização de velocidade
    if 'velocidade' in results:
        vel = results['velocidade']
        processed['velocidade'] = {
            'corrida_20m': max(0, 10 - (vel.get('corrida_20m', 0) - 2) * 2),  # 2s = 10 pontos, 7s = 0 pontos
            'agilidade': max(0, 10 - (vel.get('agilidade', 0) - 8) * 2),  # 8s = 10 pontos, 13s = 0 pontos
            'average': 0
        }
    
    # Normalização de resistência
    if 'resistencia' in results:
        res = results['resistencia']
        processed['resistencia'] = {
            'burpees': min(10, res.get('burpees', 0) / 5),  # Max 50 burpees = 10 pontos
            'cooper': min(10, res.get('cooper', 0) / 200),  # 2000m = 10 pontos
            'average': 0
        }
    
    # Normalização de coordenação
    if 'coordenacao' in results:
        coord = results['coordenacao']
        processed['coordenacao'] = {
            'equilibrio': min(10, coord.get('equilibrio', 0) / 6),  # 60s = 10 pontos
            'saltos': min(10, coord.get('saltos', 0) / 4),  # 40 saltos = 10 pontos
            'average': 0
        }
    
    # Calcula médias
    for categoria in processed:
        if processed[categoria]:
            valores = [v for k, v in processed[categoria].items() if k != 'average']
            processed[categoria]['average'] = sum(valores) / len(valores)
    
    return processed
