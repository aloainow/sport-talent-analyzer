# Importações simplificadas
from .sport_helper import get_sport_recommendations
from .test_processor import process_test_results, normalize_score, calculate_average
from .age_adjusted_calculations import get_age_group, calculate_age_adjusted_score

__all__ = [
    'get_sport_recommendations',
    'process_test_results',
    'normalize_score',
    'calculate_average',
    'get_age_group',
    'calculate_age_adjusted_score'
]
