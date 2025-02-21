import json
import os
from typing import Dict, Any

def get_age_group(age: int) -> str:
    """
    Determina o grupo de idade para os parâmetros de teste
    """
    if age <= 12:
        return "10-12"
    elif age <= 15:
        return "13-15"
    else:
        return "16-18"

def load_test_parameters():
    """
    Carrega os parâmetros de teste do arquivo de configuração
    """
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(current_dir, 'config', 'test_parameters.json')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar parâmetros de teste: {str(e)}")
        return None

def calculate_age_adjusted_score(value: float, test_type: str, test_name: str, age: int, gender: str) -> float:
    """
    Calcula o score ajustado pela idade para um teste específico
    """
    params = load_test_parameters()
    if not params:
        return 50  # valor padrão em caso de erro
        
    age_group = get_age_group(age)
    test_params = params[gender.lower()][age_group][test_type][test_name]
    
    # Encontra a classificação mais próxima
    for level in ['excelente', 'otimo', 'bom', 'regular', 'fraco']:
        if value >= test_params[level]['valor']:
            return test_params[level]['score']
    
    return test_params['fraco']['score']

def get_development_potential(age: int, current_scores: Dict[str, float]) -> float:
    """
    Calcula o potencial de desenvolvimento baseado na idade
    """
    # Quanto mais jovem, maior o potencial de desenvolvimento
    base_potential = max(0, min(100, (18 - age) * 10))
    
    # Ajusta baseado nos scores atuais
    current_avg = sum(current_scores.values()) / len(current_scores)
    
    # Potencial é maior quando há mais espaço para melhoria
    improvement_factor = (100 - current_avg) / 100
    
    return base_potential * improvement_factor

def calculate_final_score(user_data: Dict[str, Any], sport_compatibility: float) -> float:
    """
    Calcula o score final considerando idade e potencial
    """
    age = user_data.get('idade', 18)
    current_scores = {
        'biotype': user_data.get('biotype_score', 50),
        'physical': user_data.get('physical_score', 50),
        'technical': user_data.get('technical_score', 50),
        'tactical': user_data.get('tactical_score', 50)
    }
    
    # Calcula potencial de desenvolvimento
    potential = get_development_potential(age, current_scores)
    
    # Ajusta o score base com o potencial
    base_score = sport_compatibility * 0.7  # 70% do peso para compatibilidade atual
    potential_score = potential * 0.3       # 30% do peso para potencial
    
    final_score = base_score + potential_score
    
    # Garante que o score está entre 0 e 100
    return max(0, min(100, final_score))
