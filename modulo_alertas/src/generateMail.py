# Níveis de alerta de umidade e recomendações
HUMIDITY_ALERTS = {
    "atencao": {
        "range": (21, 30),
        "title": "Estado de Atenção",
        "color": "#FF9800",  # Laranja
        "recommendations": [
            "Evitar exercícios físicos ao ar livre entre 11 e 15 horas",
            "Umidificar o ambiente através de vaporizadores, toalhas molhadas, recipientes com água, molhamento de jardins, etc.",
            "Sempre que possível permanecer em locais protegidos do sol, em áreas vegetadas, etc.",
            "Consumir água à vontade"
        ]
    },
    "alerta": {
        "range": (12, 20),
        "title": "Estado de Alerta",
        "color": "#FF5722",  # Laranja escuro
        "recommendations": [
            "Observar as recomendações do estado de atenção",
            "Suprimir exercícios físicos e trabalhos ao ar livre entre 10 e 16 horas",
            "Evitar aglomerações em ambientes fechados",
            "Usar soro fisiológico para olhos e narinas"
        ]
    },
    "emergencia": {
        "range": (0, 11),
        "title": "Estado de Emergência",
        "color": "#B71C1C",  # Vermelho escuro
        "recommendations": [
            "Observar as recomendações para os estados de atenção e de alerta",
            "Determinar a interrupção de qualquer atividade ao ar livre entre 10 e 16 horas como aulas de educação física, coleta de lixo, entrega de correspondência, etc.",
            "Determinar a suspensão de atividades que exijam aglomerações de pessoas em recintos fechados como aulas, cinemas, etc., entre 10 e 16 horas",
            "Durante as tardes, manter com umidade os ambientes internos, principalmente quarto de crianças, hospitais, etc."
        ]
    }
}

# Níveis de alerta de temperatura e recomendações
TEMPERATURE_ALERTS = {
    "atencao": {
        "range": (3, 4.9),
        "title": "Estado de Atenção",
        "color": "#FF9800",  # Laranja
        "recommendations": [
            "Beba bastante água ao longo do dia",
            "Prefira roupas leves e claras",
            "Evite atividades físicas ao ar livre entre 10h e 16h",
            "Dê atenção especial a crianças, idosos e pessoas com doenças crônicas"
        ]
    },
    "alerta": {
        "range": (5, 6.9),
        "title": "Estado de Alerta",
        "color": "#FF5722",  # Laranja escuro
        "recommendations": [
            "Reduza a exposição direta ao sol, principalmente nas horas mais quentes",
            "Hidrate-se com maior frequência, mesmo sem sentir sede",
            "Mantenha os ambientes bem ventilados",
            "Evite refeições pesadas e bebidas alcoólicas",
            "Esteja atento a sinais como tontura, dor de cabeça ou cansaço excessivo"
        ]
    },
    "emergencia": {
        "range": (7, 30),
        "title": "Estado de Emergência",
        "color": "#B71C1C",  # Vermelho escuro
        "recommendations": [
            "Fique em ambientes frescos e bem ventilados sempre que possível",
            "Aumente a ingestão de água e evite sair ao ar livre durante o pico do calor",
            "Use protetor solar e chapéus se precisar sair",
            "Monitore familiares e vizinhos em situação de vulnerabilidade",
            "Em caso de mal-estar intenso, procure atendimento médico imediatamente"
        ]
    }
}

def get_humidity_alert_level(humidity_value):
    """
    Determina o nível de alerta com base no valor de umidade.
    
    Args:
        humidity_value (float): Valor da umidade em porcentagem
        
    Returns:
        dict: Informações do nível de alerta ou None se acima dos níveis de alerta
    """
    for level_key, level_info in HUMIDITY_ALERTS.items():
        min_val, max_val = level_info["range"]
        if min_val <= humidity_value <= max_val:
            return level_key, level_info
    
    return None, None

def generate_humidity_recommendations_html(humidity_value):
    """
    Gera o HTML com as recomendações baseadas no nível de umidade.
    
    Args:
        humidity_value (float): Valor da umidade em porcentagem
        
    Returns:
        str: HTML com as recomendações ou string vazia se acima dos níveis de alerta
    """
    level_key, level_info = get_humidity_alert_level(humidity_value)
    
    if not level_info:
        return ""
    
    recommendations_html = f"""
    <div style="margin-top: 20px; background-color: {level_info['color']}20; padding: 15px; border-left: 5px solid {level_info['color']}; border-radius: 3px;">
        <h3 style="color: {level_info['color']}; margin-top: 0;">{level_info['title']}</h3>
        <p><strong>Cuidados a serem tomados:</strong></p>
        <ul>
    """
    
    for rec in level_info['recommendations']:
        recommendations_html += f"<li>{rec}</li>\n"
    
    recommendations_html += """
        </ul>
    </div>
    """
    
    return recommendations_html

def get_temperature_alert_level(difference):
    """
    Determina o nível de alerta com base na diferença de temperatura.
    
    Args:
        difference (float): Diferença entre a temperatura atual e o limite
        
    Returns:
        dict: Informações do nível de alerta ou None se abaixo dos níveis de alerta
    """
    for level_key, level_info in TEMPERATURE_ALERTS.items():
        min_val, max_val = level_info["range"]
        if min_val <= difference <= max_val:
            return level_key, level_info
    
    return None, None

def generate_temperature_recommendations_html(difference):
    """
    Gera o HTML com as recomendações baseadas na diferença de temperatura.
    
    Args:
        difference (float): Diferença entre a temperatura atual e o limite
        
    Returns:
        str: HTML com as recomendações ou string vazia se abaixo dos níveis de alerta
    """
    level_key, level_info = get_temperature_alert_level(difference)
    
    if not level_info:
        return ""
    
    recommendations_html = f"""
    <div style="margin-top: 20px; background-color: {level_info['color']}20; padding: 15px; border-left: 5px solid {level_info['color']}; border-radius: 3px;">
        <h3 style="color: {level_info['color']}; margin-top: 0;">{level_info['title']}</h3>
        <p><strong>Cuidados a serem tomados:</strong></p>
        <ul>
    """
    
    for rec in level_info['recommendations']:
        recommendations_html += f"<li>{rec}</li>\n"
    
    recommendations_html += """
        </ul>
    </div>
    """
    
    return recommendations_html

def generate_temperature_alert_email(cidade_nome, valor, threshold, unit, user_id, is_max=True):
    """
    Gera o conteúdo HTML para alertas de temperatura.
    
    Args:
        cidade_nome (str): Nome da cidade para o alerta
        valor (float): Valor da temperatura detectada
        threshold (float): Limiar de temperatura (máximo ou mínimo)
        unit (str): Unidade de medida (°C)
        user_id (int): ID do usuário
        is_max (bool): True se o alerta é para máxima, False se for mínima
        difference (float): Diferença entre o valor e o limite
    Returns:
        str: Conteúdo HTML formatado para o email
    """
    tipo_alerta = "acima" if is_max else "abaixo"

    difference = valor - threshold
    
    # Gerar recomendações baseadas na diferença de temperatura
    # Só usamos as recomendações se for alerta de temperatura alta
    recommendations_html = ""
    if is_max and difference > 0:  # Só mostrar recomendações para temperatura acima do limite
        recommendations_html = generate_temperature_recommendations_html(difference)
    
    alert_data = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <div style="background-color: {'#e74c3c' if is_max else '#3498db'}; color: white; padding: 10px; text-align: center; border-radius: 5px 5px 0 0;">
            <h2>Alerta Meteorológico - Temperatura {tipo_alerta} do limite</h2>
        </div>
        <div style="padding: 20px;">
            <p><strong>Cidade:</strong> {cidade_nome}</p>
            <p><strong>Temperatura:</strong> {valor:.1f}{unit} (limite: {threshold}{unit})</p>
            
            {recommendations_html}
            
            <hr style="border: 0; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #777; font-size: 12px;">Este é um email automático do CEMPA.</p>
            <p style="color: #777; font-size: 12px;">Por favor, não responda a este email.</p>
            <div style="text-align: center; margin-top: 20px;">
                <a href="http://200.137.215.94:8081/users/delete/{user_id}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Descadastrar-se</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return alert_data

def generate_humidity_alert_email(cidade_nome, valor, threshold, unit, user_id, is_max=True):
    """
    Gera o conteúdo HTML para alertas de umidade.
    
    Args:
        cidade_nome (str): Nome da cidade para o alerta
        valor (float): Valor da umidade detectada
        threshold (float): Limiar de umidade (máximo ou mínimo)
        unit (str): Unidade de medida (%)
        user_id (int): ID do usuário
        is_max (bool): True se o alerta é para máxima, False se for mínima
    
    Returns:
        str: Conteúdo HTML formatado para o email
    """
    tipo_alerta = "acima" if is_max else "abaixo"
    
    # Gerar recomendações baseadas no valor da umidade
    # Só usamos as recomendações se for alerta de baixa umidade
    recommendations_html = ""
    if not is_max and valor < 30:  # Só mostrar recomendações para umidade baixa
        recommendations_html = generate_humidity_recommendations_html(valor)
    
    alert_data = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <div style="background-color: {'#3498db' if is_max else '#e67e22'}; color: white; padding: 10px; text-align: center; border-radius: 5px 5px 0 0;">
            <h2>Alerta Meteorológico - Umidade {tipo_alerta} do limite</h2>
        </div>
        <div style="padding: 20px;">
            <p><strong>Cidade:</strong> {cidade_nome}</p>
            <p><strong>Umidade:</strong> {valor:.1f}{unit} (limite: {threshold}{unit})</p>
            
            {recommendations_html}
            
            <hr style="border: 0; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #777; font-size: 12px;">Este é um email automático do CEMPA.</p>
            <p style="color: #777; font-size: 12px;">Por favor, não responda a este email.</p>
            <div style="text-align: center; margin-top: 20px;">
                <a href="http://200.137.215.94:8081/users/delete/{user_id}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Descadastrar-se</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return alert_data