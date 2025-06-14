from abc import ABC, abstractmethod
from typing import Optional
import os
from dotenv import load_dotenv
from pathlib import Path

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


# Carregar variável de ambiente para o canal de notificação
env_path = Path('.env')
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    parent_env_path = Path('../.env')
    if parent_env_path.exists():
        load_dotenv(dotenv_path=parent_env_path)

NOTIFICATION_CHANNEL = os.getenv('NOTIFICATION_CHANNEL', 'EMAIL').upper()

class NotificationContentStrategy(ABC):
    """Interface base para estratégias de geração de conteúdo de notificação."""
    
    @abstractmethod
    def generate_temperature_content(self, cidade_nome: str, valor: float, threshold: float, 
                                   unit: str, user_id: str, is_max: bool = True, 
                                   start_hour: Optional[str] = None,
                                   end_hour: Optional[str] = None) -> str:
        """Gera conteúdo para alerta de temperatura."""
        pass
    
    @abstractmethod
    def generate_humidity_content(self, cidade_nome: str, valor: float, threshold: float,
                                unit: str, user_id: str, is_max: bool = True,
                                start_hour: Optional[str] = None,
                                end_hour: Optional[str] = None) -> str:
        """Gera conteúdo para alerta de umidade."""
        pass

class EmailContentStrategy(NotificationContentStrategy):
    """Estratégia para geração de conteúdo em formato HTML para emails."""
    
    def __init__(self):
        self.generate_temp_recs = generate_temperature_recommendations_html
        self.generate_humidity_recs = generate_humidity_recommendations_html
    
    def generate_temperature_content(self, cidade_nome: str, valor: float, threshold: float,
                                   unit: str, user_id: str, is_max: bool = True,
                                   start_hour: Optional[str] = None,
                                   end_hour: Optional[str] = None) -> str:
        """Gera conteúdo HTML para alerta de temperatura."""
        tipo_alerta = "alta" if is_max else "baixa"
        difference = valor - threshold
        
        recommendations_html = ""
        if is_max and difference > 0:
            recommendations_html = self.generate_temp_recs(difference)
        
        # Formatar o período da previsão
        periodo_previsao = ""
        if start_hour and end_hour:
            periodo_previsao = f"entre {start_hour} e {end_hour}"
        elif start_hour:
            periodo_previsao = f"a partir de {start_hour}"
        elif end_hour:
            periodo_previsao = f"até {end_hour}"
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <div style="background-color: {'#e74c3c' if is_max else '#3498db'}; color: white; padding: 10px; text-align: center; border-radius: 5px 5px 0 0;">
                <h2>Aviso - Previsão de {tipo_alerta} temperatura</h2>
            </div>
            <div style="padding: 20px;">
                <p><strong>Cidade:</strong> {cidade_nome}</p>
                <p><strong>Temperatura:</strong> {valor:.1f}{unit}</p>
                <p><strong>Período da previsão:</strong> {periodo_previsao}</p>
                
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
    
    def generate_humidity_content(self, cidade_nome: str, valor: float, threshold: float,
                                unit: str, user_id: str, is_max: bool = True,
                                start_hour: Optional[str] = None,
                                end_hour: Optional[str] = None) -> str:
        """Gera conteúdo HTML para alerta de umidade."""
        tipo_alerta = "acima" if is_max else "abaixo"
        
        recommendations_html = ""
        if not is_max and valor < 30:
            recommendations_html = self.generate_humidity_recs(valor)
        
        # Formatar o período da previsão
        periodo_previsao = ""
        if start_hour and end_hour:
            periodo_previsao = f"entre {start_hour} e {end_hour}"
        elif start_hour:
            periodo_previsao = f"a partir de {start_hour}"
        elif end_hour:
            periodo_previsao = f"até {end_hour}"
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <div style="background-color: {'#3498db' if is_max else '#e67e22'}; color: white; padding: 10px; text-align: center; border-radius: 5px 5px 0 0;">
                <h2>Aviso - Previsão de baixa umidade relativa do ar</h2>
            </div>
            <div style="padding: 20px;">
                <p><strong>Cidade:</strong> {cidade_nome}</p>
                <p><strong>Umidade relativa do ar:</strong> {valor:.1f}{unit}</p>
                <p><strong>Período da previsão:</strong> {periodo_previsao}</p>
                
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

class SMSContentStrategy(NotificationContentStrategy):
    """Estratégia para geração de conteúdo em formato texto para SMS."""
    
    def generate_temperature_content(self, cidade_nome: str, valor: float, threshold: float,
                                   unit: str, user_id: str, is_max: bool = True,
                                   start_hour: Optional[str] = None,
                                   end_hour: Optional[str] = None) -> str:
        """Gera conteúdo texto para alerta de temperatura."""
        tipo_alerta = "alta" if is_max else "baixa"
        difference = valor - threshold
        
        # Formatar o período da previsão
        periodo_previsao = ""
        if start_hour and end_hour:
            periodo_previsao = f"entre {start_hour} e {end_hour}"
        elif start_hour:
            periodo_previsao = f"a partir de {start_hour}"
        elif end_hour:
            periodo_previsao = f"até {end_hour}"
        
        message = f"CEMPA Notify: Alerta de temperatura {tipo_alerta} em {cidade_nome}. "
        message += f"Temperatura: {valor:.1f}{unit} (limite: {threshold}{unit}). "
        message += f"Período: {periodo_previsao}. "
        
        if is_max and difference > 0:
            if difference >= 7:
                message += "Estado de Emergência! Evite atividades ao ar livre."
            elif difference >= 5:
                message += "Estado de Alerta! Reduza exposição ao sol."
            elif difference >= 3:
                message += "Estado de Atenção! Mantenha-se hidratado."
        
        message += f" Para descadastrar: http://200.137.215.94:8081/users/delete/{user_id}"
        return message
    
    def generate_humidity_content(self, cidade_nome: str, valor: float, threshold: float,
                                unit: str, user_id: str, is_max: bool = True,
                                start_hour: Optional[str] = None,
                                end_hour: Optional[str] = None) -> str:
        """Gera conteúdo texto para alerta de umidade."""
        tipo_alerta = "acima" if is_max else "abaixo"
        
        # Formatar o período da previsão
        periodo_previsao = ""
        if start_hour and end_hour:
            periodo_previsao = f"entre {start_hour} e {end_hour}"
        elif start_hour:
            periodo_previsao = f"a partir de {start_hour}"
        elif end_hour:
            periodo_previsao = f"até {end_hour}"
        
        message = f"CEMPA Notify: Alerta de umidade {tipo_alerta} em {cidade_nome}. "
        message += f"Umidade: {valor:.1f}{unit} (limite: {threshold}{unit}). "
        message += f"Período: {periodo_previsao}. "
        
        if not is_max and valor < 30:
            if valor <= 11:
                message += "Estado de Emergência! Evite atividades ao ar livre."
            elif valor <= 20:
                message += "Estado de Alerta! Mantenha ambientes umidificados."
            elif valor <= 30:
                message += "Estado de Atenção! Consuma água à vontade."
        
        message += f" Para descadastrar: http://200.137.215.94:8081/users/delete/{user_id}"
        return message

class NotificationContentFactory:
    """Factory para criar a estratégia apropriada de geração de conteúdo."""
    
    @staticmethod
    def create_strategy() -> NotificationContentStrategy:
        """
        Cria e retorna a estratégia apropriada baseada na variável de ambiente NOTIFICATION_CHANNEL.
        
        Returns:
            NotificationContentStrategy: A estratégia de geração de conteúdo apropriada
        """
        if NOTIFICATION_CHANNEL == 'SMS':
            return SMSContentStrategy()
        return EmailContentStrategy()  # EMAIL é o padrão 