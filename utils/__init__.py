# Importações dos módulos
from .test_processor import normalize_score, calculate_average, process_test_results
from .openai_helper import get_sport_recommendations

__all__ = [
    'get_sport_recommendations',
    'process_test_results',
    'normalize_score',
    'calculate_average'
]

__version__ = '1.0.0'
