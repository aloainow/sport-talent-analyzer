# utils/__init__.py

# Importações das funções necessárias
from .openai_helper import get_sport_recommendations
from .test_processor import (
    process_test_results,
    normalize_score,
    calculate_average
)

# Definição do que será exportado
__all__ = [
    'get_sport_recommendations',
    'process_test_results',
    'normalize_score',
    'calculate_average'
]
