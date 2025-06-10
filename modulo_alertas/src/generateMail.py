from datetime import datetime
import locale

# Try to set locale to Brazilian Portuguese for month names
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
    except:
        print("Não foi possível configurar o locale para português do Brasil. Usando locale padrão.")

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

def generate_temperature_alert_email(cidade_nome, valor, threshold, unit, localizacao, is_max=True, difference=0.0):
    """
    Gera o conteúdo HTML para alertas de temperatura.
    
    Args:
        cidade_nome (str): Nome da cidade para o alerta
        valor (float): Valor da temperatura detectada
        threshold (float): Limiar de temperatura (máximo ou mínimo)
        unit (str): Unidade de medida (°C)
        localizacao (str): Coordenadas da localização
        is_max (bool): True se o alerta é para máxima, False se for mínima
        difference (float): Diferença entre o valor e o limite
    Returns:
        str: Conteúdo HTML formatado para o email
    """
    now = datetime.now()
    month_name = now.strftime("%B").capitalize()
    tipo_alerta = "acima" if is_max else "abaixo"
    
    # Obter o dia da semana e o mês em português, se possível
    try:
        dia_semana = now.strftime("%A").capitalize()
    except:
        dia_semana = now.strftime("%A")
    
    alert_data = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <div style="background-color: {'#e74c3c' if is_max else '#3498db'}; color: white; padding: 10px; text-align: center; border-radius: 5px 5px 0 0;">
            <h2>Alerta Meteorológico - Temperatura {tipo_alerta} do limite</h2>
        </div>
        <div style="padding: 20px;">
            <p><strong>Cidade:</strong> {cidade_nome}</p>
            <p><strong>Valor:</strong> {valor:.1f}{unit} (limite: {threshold}{unit}, diferença do esperado: {difference:.1f}{unit})</p>
            <p><strong>Data/Hora:</strong> {dia_semana}, {now.strftime("%d/%m/%Y %H:%M:%S")}</p>
            <p><strong>Mês:</strong> {month_name}</p>
            <hr style="border: 0; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #777; font-size: 12px;">Este é um email automático do CEMPA.</p>
            <p style="color: #777; font-size: 12px;">Por favor, não responda a este email.</p>
        </div>
    </body>
    </html>
    """
    
    return alert_data

def generate_humidity_alert_email(cidade_nome, valor, threshold, unit, localizacao, is_max=True):
    """
    Gera o conteúdo HTML para alertas de umidade.
    
    Args:
        cidade_nome (str): Nome da cidade para o alerta
        valor (float): Valor da umidade detectada
        threshold (float): Limiar de umidade (máximo ou mínimo)
        unit (str): Unidade de medida (%)
        localizacao (str): Coordenadas da localização
        is_max (bool): True se o alerta é para máxima, False se for mínima
    
    Returns:
        str: Conteúdo HTML formatado para o email
    """
    now = datetime.now()
    month_name = now.strftime("%B").capitalize()
    tipo_alerta = "acima" if is_max else "abaixo"
    
    # Obter o dia da semana e o mês em português, se possível
    try:
        dia_semana = now.strftime("%A").capitalize()
    except:
        dia_semana = now.strftime("%A")
    
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
            <p><strong>Valor:</strong> {valor:.1f}{unit} (limite: {threshold}{unit})</p>
            <p><strong>Data/Hora:</strong> {dia_semana}, {now.strftime("%d/%m/%Y %H:%M:%S")}</p>
            <p><strong>Mês:</strong> {month_name}</p>
            
            {recommendations_html}
            
            <hr style="border: 0; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #777; font-size: 12px;">Este é um email automático do CEMPA.</p>
            <p style="color: #777; font-size: 12px;">Por favor, não responda a este email.</p>
        </div>
    </body>
    </html>
    """
    
    return alert_data