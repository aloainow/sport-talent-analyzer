# utils/__init__.py
# Deixe vazio por enquanto ou apenas importe o que for necessário
from .openai_helper import get_sport_recommendations
from .test_processor import process_test_results, normalize_score, calculate_average

__all__ = [
    'get_sport_recommendations',
    'process_test_results', 
    'normalize_score',
    'calculate_average'
]
