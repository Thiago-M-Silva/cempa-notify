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
        "alerts": {
            "temperature": {
                "max": 35,
                "min": 14
            },
            "umidade": {
                "max": 100,
                "min": 20
            }
        }
    },
    "Rio Verde": {
        "ibge_code": 5218805,
        "display_name": "Rio Verde",
        "alerts": {
            "temperature": {
                "max": 36,  # Valor mais alto devido ao clima mais quente da região
                "min": 15
            },
            "umidade": {
                "max": 100,
                "min": 15   # Valor mais baixo por ser região mais seca
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