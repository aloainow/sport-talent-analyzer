from config.config import TESTS_CONFIG, STYLE_CONFIG, MESSAGES

__version__ = "1.0.0"

PAGE_CONFIG = {
    "01_physical_tests": {
        "title": "Testes Físicos",
        "icon": "🏃‍♂️",
        "config": TESTS_CONFIG["physical"]
    },
    "02_technical_tests": {
        "title": "Testes Técnicos",
        "icon": "🎯",
        "config": TESTS_CONFIG["technical"]
    },
    "03_tactical_tests": {
        "title": "Testes Táticos",
        "icon": "🧠",
        "config": TESTS_CONFIG["tactical"]
    },
    "04_psychological_tests": {
        "title": "Testes Psicológicos",
        "icon": "🧪",
        "config": TESTS_CONFIG["psychological"]
    },
    "05_recommendations": {
        "title": "Recomendações",
        "icon": "⭐",
        "config": None
    }
}

def get_page_config(page_name):
    """
    Retorna a configuração específica para uma página
    """
    return PAGE_CONFIG.get(page_name, {})
