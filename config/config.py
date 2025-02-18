import os
import streamlit as st

# OpenAI Configuration
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENAI_MODEL = "gpt-4"

# Configurações do App
APP_NAME = "Analisador de Talentos Esportivos"
APP_ICON = "🏃‍♂️"
APP_VERSION = "1.0.0"

# Configurações dos Testes
TESTS_CONFIG = {
    "physical": {
        "name": "Testes Físicos",
        "tests": {
            "velocity": {
                "name": "Velocidade (20m)",
                "unit": "segundos",
                "description": "Tempo para percorrer 20 metros em linha reta",
                "min": 2.5,
                "max": 8.0
            },
            "strength": {
                "name": "Força (Flexões)",
                "unit": "repetições",
                "description": "Número máximo de flexões em 1 minuto",
                "min": 0,
                "max": 50
            },
            "endurance": {
                "name": "Resistência (Cooper)",
                "unit": "metros",
                "description": "Distância percorrida em 12 minutos",
                "min": 0,
                "max": 3000
            },
            "agility": {
                "name": "Agilidade",
                "unit": "segundos",
                "description": "Teste do quadrado (4x4m)",
                "min": 5,
                "max": 15
            }
        }
    },
    "technical": {
        "name": "Testes Técnicos",
        "tests": {
            "coordination": {
                "name": "Coordenação Motora",
                "unit": "pontos",
                "description": "Teste de coordenação motora geral",
                "min": 0,
                "max": 10
            },
            "balance": {
                "name": "Equilíbrio",
                "unit": "segundos",
                "description": "Tempo em equilíbrio em uma perna",
                "min": 0,
                "max": 60
            },
            "precision": {
                "name": "Precisão",
                "unit": "pontos",
                "description": "Teste de precisão de movimentos",
                "min": 0,
                "max": 10
            }
        }
    },
    "tactical": {
        "name": "Testes Táticos",
        "tests": {
            "decision_making": {
                "name": "Tomada de Decisão",
                "unit": "pontos",
                "description": "Avaliação de decisões em situações de jogo",
                "min": 0,
                "max": 10
            },
            "game_vision": {
                "name": "Visão de Jogo",
                "unit": "pontos",
                "description": "Capacidade de leitura e antecipação",
                "min": 0,
                "max": 10
            }
        }
    },
    "psychological": {
        "name": "Testes Psicológicos",
        "tests": {
            "motivation": {
                "name": "Motivação",
                "unit": "escala",
                "description": "Nível de motivação para prática esportiva",
                "min": 1,
                "max": 10
            },
            "teamwork": {
                "name": "Trabalho em Equipe",
                "unit": "escala",
                "description": "Capacidade de trabalhar em equipe",
                "min": 1,
                "max": 10
            },
            "leadership": {
                "name": "Liderança",
                "unit": "escala",
                "description": "Habilidades de liderança",
                "min": 1,
                "max": 10
            },
            "resilience": {
                "name": "Resiliência",
                "unit": "escala",
                "description": "Capacidade de lidar com adversidades",
                "min": 1,
                "max": 10
            },
            "concentration": {
                "name": "Concentração",
                "unit": "escala",
                "description": "Capacidade de manter o foco",
                "min": 1,
                "max": 10
            },
            "competitiveness": {
                "name": "Competitividade",
                "unit": "escala",
                "description": "Nível de espírito competitivo",
                "min": 1,
                "max": 10
            }
        }
    }
}

# Configurações de Estilo
STYLE_CONFIG = {
    "colors": {
        "primary": "#FF4B4B",
        "secondary": "#0083B8",
        "success": "#00C851",
        "warning": "#FFB300",
        "danger": "#FF4444",
        "info": "#33B5E5"
    },
    "charts": {
        "height": 400,
        "width": 600
    }
}

# Configurações do Sistema de Recomendação
RECOMMENDATION_CONFIG = {
    "min_compatibility": 70,  # Compatibilidade mínima para recomendar um esporte
    "max_recommendations": 5,  # Número máximo de recomendações
    "confidence_threshold": 0.8  # Limiar de confiança para recomendações
}

# Mensagens do Sistema
MESSAGES = {
    "welcome": """
    Bem-vindo ao Analisador de Talentos Esportivos!
    Complete os testes em cada categoria para receber recomendações personalizadas.
    """,
    "incomplete_tests": "Por favor, complete todos os testes para receber suas recomendações.",
    "processing": "Processando seus resultados...",
    "error": "Ocorreu um erro ao processar sua solicitação. Tente novamente.",
    "success": "Análise concluída com sucesso!"
}

# Cache Configuration
CACHE_CONFIG = {
    "enable": True,
    "ttl": 3600  # Time to live em segundos (1 hora)
}

def get_prompt_template():
    """
    Template para o prompt do OpenAI
    """
    return """
    Analise os seguintes resultados de testes esportivos e recomende os esportes mais adequados.
    Considere todas as características e forneça uma análise detalhada.

    Resultados dos testes:
    {test_results}

    Por favor, forneça:
    1. Top 5 esportes mais adequados
    2. Porcentagem de compatibilidade para cada esporte
    3. Pontos fortes do atleta para cada esporte
    4. Áreas que precisam de desenvolvimento
    
    Formato da resposta em JSON:
    {
        "recommendations": [
            {
                "sport": "nome do esporte",
                "compatibility": porcentagem,
                "strengths": ["ponto forte 1", "ponto forte 2"],
                "development": ["área 1", "área 2"]
            }
        ]
    }
    """

def init_session_state():
    """
    Inicializa o estado da sessão do Streamlit
    """
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {
            'physical': {},
            'technical': {},
            'tactical': {},
            'psychological': {}
        }
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
