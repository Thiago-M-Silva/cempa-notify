from abc import ABC, abstractmethod
from typing import Optional
import os
from dotenv import load_dotenv
from pathlib import Path
import math

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
    "atencao_alta": {
        "range": (3, 4.9),
        "title": "Aviso - Temperaturas Elevadas",
        "color": "#FF9800",  # Laranja
        "recommendations": [
            "Beba bastante água, mesmo sem sentir sede", 
            "Prefira roupas leves e claras",
            "Evite atividades físicas ao ar livre no período previsto de temperatura máxima elevada",
            "Reduza a exposição direta ao sol, principalmente nas horas mais quentes, use protetor solar",
            "Fique em ambientes frescos e bem ventilados sempre que possível",
            "Dê atenção especial a crianças, idosos e pessoas com doenças crônicas",
            "Monitore familiares e vizinhos em situação de vulnerabilidade",
            "Evite refeições pesadas e bebidas alcoólicas",
            "Esteja atento a sinais como tontura, dor de cabeça ou cansaço excessivo. Em caso de mal-estar intenso, procure atendimento médico imediatamente"
        ]
    },
    "alerta_alta": {
        "range": (5, 6.9),
        "title": "Aviso - Temperaturas Elevadas",
        "color": "#FF5722",  # Laranja escuro
        "recommendations": [
            "Beba bastante água, mesmo sem sentir sede", 
            "Prefira roupas leves e claras",
            "Evite atividades físicas ao ar livre no período previsto de temperatura máxima elevada",
            "Reduza a exposição direta ao sol, principalmente nas horas mais quentes, use protetor solar",
            "Fique em ambientes frescos e bem ventilados sempre que possível",
            "Dê atenção especial a crianças, idosos e pessoas com doenças crônicas",
            "Monitore familiares e vizinhos em situação de vulnerabilidade",
            "Evite refeições pesadas e bebidas alcoólicas",
            "Esteja atento a sinais como tontura, dor de cabeça ou cansaço excessivo. Em caso de mal-estar intenso, procure atendimento médico imediatamente"
        ]
    },
    "emergencia_alta": {
        "range": (7, 30),
        "title": "Aviso - Temperaturas Elevadas",
        "color": "#B71C1C",  # Vermelho escuro
        "recommendations": [
            "Beba bastante água, mesmo sem sentir sede", 
            "Prefira roupas leves e claras",
            "Evite atividades físicas ao ar livre no período previsto de temperatura máxima elevada",
            "Reduza a exposição direta ao sol, principalmente nas horas mais quentes, use protetor solar",
            "Fique em ambientes frescos e bem ventilados sempre que possível",
            "Dê atenção especial a crianças, idosos e pessoas com doenças crônicas",
            "Monitore familiares e vizinhos em situação de vulnerabilidade",
            "Evite refeições pesadas e bebidas alcoólicas",
            "Esteja atento a sinais como tontura, dor de cabeça ou cansaço excessivo. Em caso de mal-estar intenso, procure atendimento médico imediatamente"
        ]
    },
    "atencao_baixa": {
        "range": (-4.9, -3),
        "title": "Aviso - Previsão de Temperatura Mínima Baixa",
        "color": "#2196F3",  # Azul
        "recommendations": [
            "Mantenha-se hidratado, não deixe de beber àgua",
            "Busque se agasalhar bem",
            "Evite tomar banhos com àgua muito quente", 
            "Mantenha a pele sempre hidratada",
            "Proteja-se do frio, mas tente manter o ambiente arejado",
            "Mantenha-se seco e evite arrefecer com a roupa transpirada no corpo", 
            "Dê atenção especial a crianças, idosos e pessoas com doenças crônicas no período de mínimas temperaturas"
        ]
    },
    "alerta_baixa": {
        "range": (-6.9, -5),
        "title": "Aviso - Previsão de Temperatura Mínima Baixa",
        "color": "#1976D2",  # Azul escuro
        "recommendations": [
            "Mantenha-se hidratado, não deixe de beber àgua",
            "Busque se agasalhar bem",
            "Evite tomar banhos com àgua muito quente", 
            "Mantenha a pele sempre hidratada",
            "Proteja-se do frio, mas tente manter o ambiente arejado",
            "Mantenha-se seco e evite arrefecer com a roupa transpirada no corpo", 
            "Dê atenção especial a crianças, idosos e pessoas com doenças crônicas no período de mínimas temperaturas"
        ]
    },
    "emergencia_baixa": {
        "range": (-30, -7),
        "title": "Aviso - Previsão de Temperatura Mínima Baixa",
        "color": "#0D47A1",  # Azul muito escuro
        "recommendations": [
            "Mantenha-se hidratado, não deixe de beber àgua",
            "Busque se agasalhar bem",
            "Evite tomar banhos com àgua muito quente", 
            "Mantenha a pele sempre hidratada",
            "Proteja-se do frio, mas tente manter o ambiente arejado",
            "Mantenha-se seco e evite arrefecer com a roupa transpirada no corpo", 
            "Dê atenção especial a crianças, idosos e pessoas com doenças crônicas no período de mínimas temperaturas"
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

def get_temperature_alert_level(difference, is_max=True):
    """
    Determina o nível de alerta com base na diferença de temperatura.
    
    Args:
        difference (float): Diferença entre a temperatura e o limite
        is_max (bool): Se True, verifica alertas de temperatura alta, se False, verifica alertas de temperatura baixa
        
    Returns:
        tuple: (chave do nível, informações do nível) ou (None, None) se fora dos níveis de alerta
    """
    prefix = "alta" if is_max else "baixa"
    
    for level_key, level_info in TEMPERATURE_ALERTS.items():
        if level_key.endswith(prefix):
            min_val, max_val = level_info["range"]
            if is_max:
                if min_val <= difference <= max_val:
                    return level_key, level_info
            else:
                # Para temperatura baixa, a diferença é negativa
                # Quando difference = valor - threshold e valor < threshold, difference < 0
                # Precisamos verificar se a diferença está dentro do range definido
                if min_val <= difference <= max_val:
                    return level_key, level_info
    
    return None, None

def generate_temperature_recommendations_html(difference, is_max=True):
    """
    Gera o HTML com as recomendações baseadas na diferença de temperatura.
    
    Args:
        difference (float): Diferença entre a temperatura e o limite
        is_max (bool): Se True, gera recomendações para temperatura alta, se False, para temperatura baixa
        
    Returns:
        str: HTML com as recomendações ou string vazia se fora dos níveis de alerta
    """
    level_key, level_info = get_temperature_alert_level(difference, is_max)
    
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
                                   end_hour: Optional[str] = None,
                                   data: Optional[str] = None) -> str:
        """Gera conteúdo para alerta de temperatura."""
        pass
    
    @abstractmethod
    def generate_humidity_content(self, cidade_nome: str, valor: float, threshold: float,
                                unit: str, user_id: str, is_max: bool = True,
                                start_hour: Optional[str] = None,
                                end_hour: Optional[str] = None,
                                data: Optional[str] = None) -> str:
        """Gera conteúdo para alerta de umidade."""
        pass

class EmailContentStrategy(NotificationContentStrategy):
    """Estratégia para geração de conteúdo em formato HTML para emails."""
    
    def __init__(self):
        self.generate_temp_recs = generate_temperature_recommendations_html
        self.generate_humidity_recs = generate_humidity_recommendations_html
    
    def generate_temperature_content(self, cidade_nome: str, valor: float, threshold: float,
                                   unit: str, user_email: str, is_max: bool = True,
                                   start_hour: Optional[str] = None,
                                   end_hour: Optional[str] = None,
                                   data: Optional[str] = None) -> str:
        """Gera conteúdo HTML para alerta de temperatura."""
        tipo_alerta = "temperaturas elevadas" if is_max else "temperaturas baixas"
        difference = valor - threshold
        
        recommendations_html = ""
        if (is_max and difference > 0) or (not is_max and difference < 0):
            recommendations_html = self.generate_temp_recs(difference, is_max)
        
        # Formatar o período da previsão
        periodo_previsao = ""
        if start_hour and end_hour:
            periodo_previsao = f"entre {start_hour} e {end_hour}"
        elif start_hour:
            periodo_previsao = f"a partir de {start_hour}"
        elif end_hour:
            periodo_previsao = f"até {end_hour}"
        
        # Adicionar data se fornecida
        data_html = f'<p><strong>Data:</strong> {data}</p>\n' if data else ''
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <div style="background-color: {'#e74c3c' if is_max else '#3498db'}; color: white; padding: 10px; text-align: center; border-radius: 5px 5px 0 0;">
                <h2>Aviso - Previsão de {tipo_alerta}</h2>
            </div>
            <div style="padding: 20px;">
                <p><strong>Cidade:</strong> {cidade_nome}</p>
                {data_html}
                <p>{'Temperatura máxima prevista' if is_max else 'Temperatura mínima prevista'} é de <strong> {math.ceil(valor) if is_max else math.floor(valor)}{unit} </strong> no período entre <strong>{periodo_previsao}</strong></p>
                
                
                {recommendations_html}
                
                <hr style="border: 0; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #777; font-size: 12px;">Este é um email automático do CEMPA.</p>
                <p style="color: #777; font-size: 12px;">Por favor, não responda a este email.</p>
                <div style="text-align: center; margin-top: 20px;">
                    <a href="http://200.137.215.94?email={user_email}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Descadastrar ou atualizar</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    def generate_humidity_content(self, cidade_nome: str, valor: float, threshold: float,
                                unit: str, user_email: str, is_max: bool = True,
                                start_hour: Optional[str] = None,
                                end_hour: Optional[str] = None,
                                data: Optional[str] = None) -> str:
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
        
        # Adicionar data se fornecida
        data_html = f'<p><strong>Data:</strong> {data}</p>\n' if data else ''
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <div style="background-color: {'#3498db' if is_max else '#e67e22'}; color: white; padding: 10px; text-align: center; border-radius: 5px 5px 0 0;">
                <h2>Aviso - Previsão de baixa umidade relativa do ar</h2>
            </div>
            <div style="padding: 20px;">
                <p><strong>Cidade:</strong> {cidade_nome}</p>
                {data_html}
                <p>A mínima umidade relativa prevista é de <strong>{math.floor(valor)}{unit}</strong> no período <strong>{periodo_previsao}</strong></p>
                
                
                {recommendations_html}
                
                <hr style="border: 0; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #777; font-size: 12px;">Este é um email automático do CEMPA.</p>
                <p style="color: #777; font-size: 12px;">Por favor, não responda a este email.</p>
                <div style="text-align: center; margin-top: 20px;">
                    <a href="http://200.137.215.94?email={user_email}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Descadastrar ou atualizar</a>
                </div>
            </div>
        </body>
        </html>
        """

class SMSContentStrategy(NotificationContentStrategy):
    """Estratégia para geração de conteúdo em formato texto para SMS."""
    
    def generate_temperature_content(self, cidade_nome: str, valor: float, threshold: float,
                                   unit: str, user_email: str, is_max: bool = True,
                                   start_hour: Optional[str] = None,
                                   end_hour: Optional[str] = None,
                                   data: Optional[str] = None) -> str:
        """Gera conteúdo texto para alerta de temperatura."""
        tipo_alerta = "temperaturas elevadas" if is_max else "baixa temperatura"
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
        message += f"Temperatura: {math.ceil(valor) if is_max else math.floor(valor)}{unit} (limite: {threshold}{unit}). "
        if data:
            message += f"Data: {data}. "
        message += f"Período: {periodo_previsao}. "
        
        if is_max and difference > 0:
            if difference >= 7:
                message += "Estado de Emergência! Evite atividades ao ar livre."
            elif difference >= 5:
                message += "Estado de Alerta! Reduza exposição ao sol."
            elif difference >= 3:
                message += "Estado de Atenção! Mantenha-se hidratado."
        elif not is_max and difference < 0:
            if difference <= -7:
                message += "Estado de Emergência! Evite exposição ao frio."
            elif difference <= -5:
                message += "Estado de Alerta! Use roupas adequadas."
            elif difference <= -3:
                message += "Estado de Atenção! Mantenha-se aquecido."
        
        message += f" Para descadastrar: http://200.137.215.94?email={user_email}"
        return message
    
    def generate_humidity_content(self, cidade_nome: str, valor: float, threshold: float,
                                unit: str, user_email: str, is_max: bool = True,
                                start_hour: Optional[str] = None,
                                end_hour: Optional[str] = None,
                                data: Optional[str] = None) -> str:
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
        message += f"Umidade: {math.floor(valor)}{unit} (limite: {threshold}{unit}). "
        if data:
            message += f"Data: {data}. "
        message += f"Período: {periodo_previsao}. "
        
        if not is_max and valor < 30:
            if valor <= 11:
                message += "Estado de Emergência! Evite atividades ao ar livre."
            elif valor <= 20:
                message += "Estado de Alerta! Mantenha ambientes umidificados."
            elif valor <= 30:
                message += "Estado de Atenção! Consuma água à vontade."
        
        message += f" Para descadastrar: http://200.137.215.94?email={user_email}"
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