import streamlit as st

# OpenAI Configuration
OPENAI_MODEL = "gpt-4-turbo-preview"

# Configurações do App
APP_NAME = "Analisador de Talentos Esportivos"
APP_ICON = "🏃‍♂️"
APP_VERSION = "1.0.0"

# Configurações dos Testes
TESTS_CONFIG = {
    "dados_fisicos": {
        "name": "Dados Físicos",
        "icon": "💪",
        "tests": {
            "velocidade": {
                "name": "Velocidade (20m)",
                "unit": "segundos",
                "description": "Tempo para percorrer 20 metros em linha reta",
                "min": 3.0,
                "max": 6.0,
                "reference": {
                    "iniciante": ">4.0s",
                    "intermediario": "3.5-4.0s",
                    "avancado": "<3.5s"
                }
            },
            "forca_superior": {
                "name": "Força Superior (Flexões)",
                "unit": "repetições",
                "description": "Número máximo de flexões em 1 minuto",
                "min": 0,
                "max": 50,
                "reference": {
                    "iniciante": "10-15",
                    "intermediario": "16-25",
                    "avancado": "26+"
                }
            },
            "forca_inferior": {
                "name": "Força Inferior (Agachamentos)",
                "unit": "repetições",
                "description": "Número máximo de agachamentos em 1 minuto",
                "min": 0,
                "max": 60,
                "reference": {
                    "iniciante": "20-30",
                    "intermediario": "31-40",
                    "avancado": "41+"
                }
            }
        }
    },
    "habilidades_tecnicas": {
        "name": "Habilidades Técnicas",
        "icon": "🎯",
        "tests": {
            "coordenacao": {
                "name": "Coordenação (Pular Corda)",
                "unit": "alternâncias",
                "description": "Número de alternâncias em 30 segundos",
                "min": 0,
                "max": 50,
                "reference": {
                    "iniciante": "<20",
                    "intermediario": "20-30",
                    "avancado": ">30"
                }
            },
            "precisao": {
                "name": "Precisão (Alvos)",
                "unit": "acertos",
                "description": "Número de acertos em 10 tentativas",
                "min": 0,
                "max": 10,
                "reference": {
                    "iniciante": "3-4",
                    "intermediario": "5-7",
                    "avancado": "8-10"
                }
            },
            "agilidade": {
                "name": "Agilidade (Teste do Quadrado)",
                "unit": "segundos",
                "description": "Tempo no teste do quadrado 4x4m",
                "min": 8,
                "max": 15,
                "reference": {
                    "iniciante": ">12s",
                    "intermediario": "10-12s",
                    "avancado": "<10s"
                }
            },
            "equilibrio": {
                "name": "Equilíbrio",
                "unit": "segundos",
                "description": "Tempo em equilíbrio em uma perna",
                "min": 0,
                "max": 120,
                "reference": {
                    "iniciante": "<20s",
                    "intermediario": "20-40s",
                    "avancado": ">40s"
                }
            }
        }
    },
    "aspectos_taticos": {
        "name": "Aspectos Táticos",
        "icon": "🧠",
        "tests": {
            "tomada_decisao": {
                "name": "Tomada de Decisão",
                "unit": "acertos",
                "description": "Acertos em teste de reação",
                "min": 0,
                "max": 10,
                "reference": {
                    "iniciante": "3-4",
                    "intermediario": "5-7",
                    "avancado": "8-10"
                }
            },
            "visao_jogo": {
                "name": "Visão de Jogo",
                "unit": "acertos",
                "description": "Acertos em teste de memorização",
                "min": 0,
                "max": 10,
                "reference": {
                    "iniciante": "3-4",
                    "intermediario": "5-7",
                    "avancado": "8-10"
                }
            },
            "posicionamento": {
                "name": "Posicionamento",
                "unit": "escala",
                "description": "Precisão no posicionamento",
                "min": 1,
                "max": 10,
                "reference": {
                    "iniciante": "1-3",
                    "intermediario": "4-7",
                    "avancado": "8-10"
                }
            }
        }
    },
    "fatores_psicologicos": {
        "name": "Fatores Psicológicos",
        "icon": "🎯",
        "tests": {
            "motivacao": {
                "name": "Motivação",
                "unit": "escala",
                "components": {
                    "dedicacao": {
                        "name": "Dedicação aos treinos",
                        "min": 1,
                        "max": 10
                    },
                    "frequencia": {
                        "name": "Frequência de prática",
                        "min": 1,
                        "max": 10
                    },
                    "comprometimento": {
                        "name": "Comprometimento com objetivos",
                        "min": 1,
                        "max": 10
                    }
                }
            },
            "resiliencia": {
                "name": "Resiliência",
                "unit": "escala",
                "components": {
                    "derrotas": {
                        "name": "Lidar com derrotas",
                        "min": 1,
                        "max": 10
                    },
                    "criticas": {
                        "name": "Reação a críticas",
                        "min": 1,
                        "max": 10
                    },
                    "erros": {
                        "name": "Recuperação de erros",
                        "min": 1,
                        "max": 10
                    }
                }
            },
            "trabalho_equipe": {
                "name": "Trabalho em Equipe",
                "unit": "escala",
                "components": {
                    "comunicacao": {
                        "name": "Comunicação em grupo",
                        "min": 1,
                        "max": 10
                    },
                    "opinioes": {
                        "name": "Lidar com diferentes opiniões",
                        "min": 1,
                        "max": 10
                    },
                    "contribuicao": {
                        "name": "Contribuição para objetivos coletivos",
                        "min": 1,
                        "max": 10
                    }
                }
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
    "confidence_threshold": 0.8,  # Limiar de confiança para recomendações
    "sports_data_path": "data/sport_profiles.json"  # Caminho para o arquivo de perfis dos esportes
}

# Mensagens do Sistema
MESSAGES = {
    "welcome": """
    Bem-vindo ao Analisador de Talentos Esportivos!
    Complete os testes em cada categoria para receber recomendações personalizadas.
    """,
    "incomplete_tests": "Por favor, complete todos os testes para receber suas recomendações.",
    "processing": "Analisando seus resultados...",
    "error": "Ocorreu um erro ao processar sua solicitação. Tente novamente.",
    "success": "Análise concluída com sucesso!",
    "save_success": "Resultados salvos com sucesso!",
    "test_instructions": "Complete os testes abaixo. Realize cada teste conforme as instruções."
}

def get_prompt_template():
    """
    Template para o prompt do OpenAI
    """
    return """
    Atue como um especialista em identificação de talentos esportivos.
    Analise os seguintes resultados de testes e recomende os esportes mais adequados:

    Dados Físicos:
    {dados_fisicos}

    Habilidades Técnicas:
    {habilidades_tecnicas}

    Aspectos Táticos:
    {aspectos_taticos}

    Fatores Psicológicos:
    {fatores_psicologicos}

    Com base nos dados do arquivo sport_profiles.json e nos resultados acima:
    1. Identifique os 5 esportes mais compatíveis
    2. Calcule a porcentagem de compatibilidade
    3. Liste os pontos fortes específicos para cada esporte
    4. Sugira áreas para desenvolvimento

    Retorne apenas o JSON no seguinte formato:
    {
        "recommendations": [
            {
                "name": "nome do esporte",
                "compatibility": porcentagem,
                "strengths": ["ponto forte 1", "ponto forte 2"],
                "development": ["área 1", "área 2"]
            }
        ]
    }
    """
