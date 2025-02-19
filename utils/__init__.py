"""
Módulo de utilidades para o Analisador de Talentos Esportivos.
Fornece funções para processamento de testes e recomendações de esportes.
"""

try:
    from .openai_helper import get_sport_recommendations
    from .test_processor import (
        process_test_results,
        normalize_score,
        calculate_average
    )
except ImportError as e:
    import streamlit as st
    st.error(f"Erro ao importar módulos de utilidades: {str(e)}")
    raise

__all__ = [
    'get_sport_recommendations',
    'process_test_results',
    'normalize_score',
    'calculate_average'
]

# Versão do módulo
__version__ = '1.0.0'
