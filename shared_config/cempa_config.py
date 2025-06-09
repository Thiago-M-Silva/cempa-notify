"""
Configurações globais compartilhadas entre os módulos do sistema CEMPA-Notify.

Este arquivo contém definições que devem ser consistentes em todo o sistema,
como listas de cidades válidas, tipos de alertas, e configurações de validação.
"""

# Cidades permitidas no sistema com suas informações
VALID_CITIES = {
    "Goiânia": {
        "ibge_code": 5208707,
        "display_name": "Goiânia",
        "db_name": "Goiania",
        "alerts": {
            "temperature": {
                # Default thresholds (used as fallback)
                "max": 35,
                "min": -50,
                # Monthly thresholds (1-12 representing Jan-Dec)
                "monthly": {
                    "1": {"max": 33, "min": 18},  # Janeiro
                    "2": {"max": 33, "min": 18},  # Fevereiro
                    "3": {"max": 32, "min": 17},  # Março
                    "4": {"max": 31, "min": 16},  # Abril
                    "5": {"max": 30, "min": 15},  # Maio
                    "6": {"max": 29, "min": 13},  # Junho
                    "7": {"max": 29, "min": 12},  # Julho
                    "8": {"max": 31, "min": 13},  # Agosto
                    "9": {"max": 33, "min": 15},  # Setembro
                    "10": {"max": 34, "min": 17}, # Outubro
                    "11": {"max": 33, "min": 18}, # Novembro
                    "12": {"max": 33, "min": 18}  # Dezembro
                }
            },
            "humidity": {
                "max": 100,
                "min": 30   # Alertas abaixo de 30% (estado de atenção)
            }
        }
    },
    "Rio Verde": {
        "ibge_code": 5218805,
        "display_name": "Rio Verde",
        "db_name": "Rio_Verde",
        "alerts": {
            "temperature": {
                # Default thresholds (used as fallback)
                "max": 36,  # Valor mais alto devido ao clima mais quente da região
                "min": 15,
                # Monthly thresholds (1-12 representing Jan-Dec)
                "monthly": {
                    "1": {"max": 20, "min": 17},  # Janeiro
                    "2": {"max": 20, "min": 17},  # Fevereiro
                    "3": {"max": 20, "min": 16},  # Março
                    "4": {"max": 20, "min": 15},  # Abril
                    "5": {"max": 20, "min": 14},  # Maio
                    "6": {"max": 20, "min": 12},  # Junho
                    "7": {"max": 20, "min": 11},  # Julho
                    "8": {"max": 20, "min": 12},  # Agosto
                    "9": {"max": 20, "min": 14},  # Setembro
                    "10": {"max": 20, "min": 16}, # Outubro
                    "11": {"max": 20, "min": 17}, # Novembro
                    "12": {"max": 20, "min": 17}  # Dezembro
                }
            },
            "humidity": {
                "max": 100,
                "min": 30   # Alertas abaixo de 30% (estado de atenção)
            }
        }
    }
}

# Lista de nomes de cidades para uso em validações e seleções
CITY_NAMES = list(VALID_CITIES.keys())

# Tipos de alertas disponíveis
VALID_ALERT_TYPES = [
    "temperature",
    "humidity",
]

# Mensagens de erro para validações
ERROR_MESSAGES = {
    "invalid_city": f"Cidade inválida. Escolha uma das seguintes opções: {', '.join(CITY_NAMES)}",
    "invalid_alert": f"Tipo de alerta inválido. Escolha um dos seguintes: {', '.join(VALID_ALERT_TYPES)}",
    "email_exists": "Este email já está cadastrado no sistema.",
    "username_exists": "Este nome de usuário já está em uso.",
    "required_field": "Este campo é obrigatório.",
    "invalid_email": "Formato de email inválido."
} 