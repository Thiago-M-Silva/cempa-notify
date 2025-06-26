import os
import pandas as pd
from datetime import datetime, timedelta
from meteogram_parser import MeteogramParser
from sendEmail import EmailSender
from notification_content import NotificationContentFactory
from file_utils import clean_old_files, download_meteogram_file
import sys
import math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from modulo_usuarios.src import create_app
from modulo_usuarios.src.services import AlertService
from shared_config.config_parser import ConfigParser

minimum_diff_temperature_min = 3.0

class AlertGenerator:
    """
    Classe para gerar alertas com base em dados meteorológicos.
    Utiliza ConfigParser e MeteogramParser para obter dados e configurações.
    Monitora temperatura e umidade, gerando alertas únicos por cidade e tipo.
    """
    
    def __init__(self, config_path=None, meteogram_path=None, alert_service=None):
        """
        Inicializa o gerador de alertas.
        
        Args:
            config_path (str, optional): Caminho para o arquivo de configuração
            meteogram_path (str, optional): Caminho para o arquivo de meteograma
            alert_service (object, optional): Serviço para buscar usuários para notificação
        """
        # Inicializar componentes
        self.config = ConfigParser(config_path)
        self.config.parse()
        self.config_map = self.config.get_config_map()
        self.email_sender = EmailSender()
        self.alert_service = alert_service
        
        # Inicializar a estratégia de geração de conteúdo
        self.content_strategy = NotificationContentFactory.create_strategy()
        
        # Configurar o parser de meteograma
        self.meteogram_path = meteogram_path
        self.meteogram_parser = None
        self.meteogram_data = None
        
        # Armazenar alertas gerados (para evitar duplicação)
        # Estrutura: {cidade: {tipo_alerta: dados_alerta}}
        self.alerts = {}
        
        # Inicializar o parser de meteograma se o caminho foi fornecido
        if self.meteogram_path:
            self._init_meteogram_parser()
        else:
            # Tentar encontrar automaticamente o arquivo de meteograma
            self._find_meteogram_file()
    
    def _find_meteogram_file(self):
        """
        Tenta encontrar o arquivo de meteograma mais recente na pasta padrão.
        
        Raises:
            FileNotFoundError: Se nenhum arquivo de meteograma for encontrado
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tmp_dir = os.path.abspath(os.path.join(current_dir, "..", "tmp_files"))
        
        if not os.path.exists(tmp_dir):
            error_msg = f"Diretório de arquivos temporários não encontrado: {tmp_dir}"
            print(f"ERRO: {error_msg}")
            raise FileNotFoundError(error_msg)
        
        meteogram_files = [
            os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir)
            if f.startswith("HST") and f.endswith("MeteogramASC.out")
        ]
        
        if not meteogram_files:
            error_msg = f"Nenhum arquivo de meteograma encontrado em: {tmp_dir}"
            print(f"ERRO: {error_msg}")
            raise FileNotFoundError(error_msg)
        
        # Ordenar por data de modificação (mais recente primeiro)
        meteogram_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        self.meteogram_path = meteogram_files[0]
        print(f"Arquivo de meteograma encontrado: {self.meteogram_path}")
        
        try:
            self._init_meteogram_parser()
        except (FileNotFoundError, ValueError) as e:
            print(f"ERRO ao inicializar parser com o arquivo encontrado: {str(e)}")
            raise
    
    def _init_meteogram_parser(self):
        """
        Inicializa o parser de meteograma com o arquivo definido.
        
        Raises:
            FileNotFoundError: Se o arquivo de meteograma não for encontrado
            ValueError: Se o caminho do arquivo não for fornecido
        """
        try:
            self.meteogram_parser = MeteogramParser(self.meteogram_path)
            print(f"Parser de meteograma inicializado com o arquivo: {self.meteogram_path}")
        except (FileNotFoundError, ValueError) as e:
            print(f"ERRO: {str(e)}")
            self.meteogram_parser = None
            raise
    
    def kelvin_to_celsius(self, temp_k):
        """
        Converte temperatura de Kelvin para Celsius.
        
        Args:
            temp_k (float): Temperatura em Kelvin
            
        Returns:
            float: Temperatura em Celsius
        """
        return temp_k - 273.15
    
    def calculate_relative_humidity(self, t_max, td_max):
        """
        Calcula a umidade relativa usando a fórmula de Magnus-Tetens.
        
        Args:
            t_max (float): Temperatura máxima em Celsius
            td_max (float): Temperatura do ponto de orvalho em Celsius
            
        Returns:
            float: Umidade relativa em porcentagem (0-100)
        """
        # Constantes para a fórmula de Magnus-Tetens
        a = 17.27
        b = 237.7
        
        # Calcular pressão de saturação para temperatura e ponto de orvalho
        es_t = 6.112 * math.exp((a * t_max) / (t_max + b))
        es_td = 6.112 * math.exp((a * td_max) / (td_max + b))
        
        # Calcular umidade relativa em porcentagem
        rh = (es_td / es_t) * 100
        
        # Limitar a umidade entre 0 e 100%
        return max(0, min(100, rh))
    
    def load_meteogram_data(self):
        """
        Carrega os dados do meteograma.
        
        Returns:
            dict: Dados do meteograma
            
        Raises:
            FileNotFoundError: Se nenhum arquivo de meteograma for encontrado
            Exception: Se ocorrer erro ao carregar os dados
        """
        if not self.meteogram_parser:
            if not self.meteogram_path:
                # Tentar encontrar um arquivo automaticamente
                self._find_meteogram_file()
            else:
                # Inicializar com o arquivo já definido
                self._init_meteogram_parser()
            
            if not self.meteogram_parser:
                error_msg = "Não foi possível inicializar o parser de meteograma"
                print(f"ERRO: {error_msg}")
                raise FileNotFoundError(error_msg)
        
        try:
            self.meteogram_data = self.meteogram_parser.parse()
            print(f"Dados do meteograma carregados: {len(self.meteogram_data)} polígonos encontrados")
            return self.meteogram_data
        except Exception as e:
            error_msg = f"Erro ao carregar dados do meteograma: {str(e)}"
            print(f"ERRO: {error_msg}")
            raise Exception(error_msg) from e

    def check_temperature_alerts(self, date=None):
        """
        Verifica se há alertas de temperatura baseados nos limiares configurados.
        Gera alertas apenas quando a diferença entre a temperatura e o limiar
        é maior ou igual a minimum_diff_temperature_min.
        
        Args:
            date (datetime, optional): Data para determinar o mês.
                Se None, usa a data atual.
        
        Returns:
            dict: Dicionário com alertas de temperatura por cidade
        """
        if not self.meteogram_data:
            self.load_meteogram_data()
            if not self.meteogram_data:
                return {}
        
        # Se a data não for especificada, usar a data atual
        if date is None:
            date = datetime.now()
        
        month = date.month
        alerts = {}
        
        # Para cada polígono na configuração
        for polygon_name, config_data in self.config_map.items():
            display_name = self.config.get_display_name(polygon_name)
            
            if not display_name:
                continue  # Pular se não tiver nome de exibição
            
            # Obter os limiares de temperatura para este mês
            max_threshold = self.config.get_monthly_temp_threshold(polygon_name, month)
            min_threshold = self.config.get_monthly_temp_min_threshold(polygon_name, month)
            
            # Ignorar limiares que são 0, pois indicam que não há limite configurado
            if max_threshold == 0:
                max_threshold = None
            if min_threshold == 0:
                min_threshold = None
            
            if not max_threshold and not min_threshold:
                continue  # Pular se não tiver limiares configurados válidos
            
            # Verificar se o polígono existe nos dados do meteograma
            if polygon_name not in self.meteogram_data:
                continue  # Pular se não tiver dados para este polígono
            
            time_data = self.meteogram_data[polygon_name]
            
            # Inicializar o alerta para esta cidade se ainda não existir
            if display_name not in alerts:
                alerts[display_name] = {}
            
            # Verificar cada registro de tempo
            max_temp_c = float('-inf')
            min_temp_c = float('inf')
            max_temp_data = None
            min_temp_data = None
            
            for seconds, values in time_data.items():
                if 'Tmax' in values and 'Tmin' in values:
                    # Converter de Kelvin para Celsius
                    temp_max_k = values['Tmax']
                    temp_min_k = values['Tmin']
                    temp_max_c = self.kelvin_to_celsius(temp_max_k)
                    temp_min_c = self.kelvin_to_celsius(temp_min_k)
                    
                    # Verificar temperatura máxima
                    if max_threshold:
                        diff_max = temp_max_c - max_threshold
                        if temp_max_c > max_temp_c and diff_max >= minimum_diff_temperature_min:
                            max_temp_c = temp_max_c
                            max_temp_data = {
                                'polygon_name': polygon_name,
                                'seconds': seconds,
                                'date': values.get('date', 'N/A'),
                                'temp_k': temp_max_k,
                                'temp_c': temp_max_c,
                                'threshold': max_threshold,
                                'difference': diff_max
                            }
                    
                    # Verificar temperatura mínima
                    if min_threshold:
                        diff_min = temp_min_c - min_threshold
                        if temp_min_c < min_temp_c and diff_min <= -minimum_diff_temperature_min:
                            min_temp_c = temp_min_c
                            min_temp_data = {
                                'polygon_name': polygon_name,
                                'seconds': seconds,
                                'date': values.get('date', 'N/A'),
                                'temp_k': temp_min_k,
                                'temp_c': temp_min_c,
                                'threshold': min_threshold,
                                'difference': diff_min
                            }
            
            # Se encontrou temperatura acima do limiar máximo
            if max_threshold and max_temp_c > max_threshold and max_temp_data:
                alerts[display_name]['temperature_high'] = {
                    'value': max_temp_c,
                    'value_k': max_temp_data['temp_k'],
                    'threshold': max_threshold,
                    'difference': max_temp_data['difference'],
                    'date': max_temp_data['date'],
                    'seconds': max_temp_data['seconds'],
                    'polygon_name': polygon_name
                }
            
            # Se encontrou temperatura abaixo do limiar mínimo
            if min_threshold and min_temp_c < min_threshold and min_temp_data:
                alerts[display_name]['temperature_low'] = {
                    'value': min_temp_c,
                    'value_k': min_temp_data['temp_k'],
                    'threshold': min_threshold,
                    'difference': min_temp_data['difference'],
                    'date': min_temp_data['date'],
                    'seconds': min_temp_data['seconds'],
                    'polygon_name': polygon_name
                }
        
        # Filtrar apenas as cidades com alertas
        return {city: data for city, data in alerts.items() if data}
    
    def check_humidity_alerts(self, min_threshold=30, max_threshold=90, date=None):
        """
        Verifica se há alertas de umidade baseados nos limiares especificados.
        Gera alertas apenas para umidade baixa (abaixo do limiar mínimo).
        Calcula a umidade relativa a partir de Tave e TDave usando a fórmula de Magnus-Tetens.
        
        Args:
            min_threshold (float): Limiar mínimo de umidade (%)
            max_threshold (float): Limiar máximo de umidade (%) - não utilizado
            date (datetime, optional): Data de referência
        
        Returns:
            dict: Dicionário com alertas de umidade por cidade
        """
        if not self.meteogram_data:
            self.load_meteogram_data()
            if not self.meteogram_data:
                return {}
        
        alerts = {}
        
        # Para cada polígono na configuração
        for polygon_name, config_data in self.config_map.items():
            display_name = self.config.get_display_name(polygon_name)
            
            if not display_name:
                continue  # Pular se não tiver nome de exibição
            
            # Verificar se o polígono existe nos dados do meteograma
            if polygon_name not in self.meteogram_data:
                continue  # Pular se não tiver dados para este polígono
            
            time_data = self.meteogram_data[polygon_name]
            
            # Inicializar o alerta para esta cidade se ainda não existir
            if display_name not in alerts:
                alerts[display_name] = {}
            
            # Verificar cada registro de tempo
            min_humidity = float('inf')
            min_humidity_data = None
            
            for seconds, values in time_data.items():
                # Verificar se temos os dados necessários para calcular a umidade relativa
                if 'Tave' in values and 'TDave' in values:
                    # Converter para Celsius se estão em Kelvin
                    t_ave_celsius = self.kelvin_to_celsius(values['Tave'])
                    td_ave_celsius = self.kelvin_to_celsius(values['TDave'])
                    
                    # Calcular a umidade relativa
                    humidity = self.calculate_relative_humidity(t_ave_celsius, td_ave_celsius)
                    
                    # Atualizar a umidade mínima
                    if humidity < min_humidity:
                        min_humidity = humidity
                        min_humidity_data = {
                            'polygon_name': polygon_name,
                            'seconds': seconds,
                            'date': values.get('date', 'N/A'),
                            'humidity': humidity,
                            'threshold': min_threshold,
                            'difference': humidity - min_threshold,
                            'tave': t_ave_celsius,
                            'tdave': td_ave_celsius
                        }
            
            # Verificar se há alertas de umidade baixa
            if min_humidity < min_threshold and min_humidity_data:
                alerts[display_name]['humidity_low'] = {
                    'value': min_humidity,
                    'threshold': min_threshold,
                    'difference': min_humidity - min_threshold,
                    'date': min_humidity_data['date'],
                    'seconds': min_humidity_data['seconds'],
                    'polygon_name': polygon_name
                }
                
                # Adicionar detalhes de temperatura se disponíveis
                if 'tave' in min_humidity_data and 'tdave' in min_humidity_data:
                    alerts[display_name]['humidity_low']['tave'] = min_humidity_data['tave']
                    alerts[display_name]['humidity_low']['tdave'] = min_humidity_data['tdave']
        
        # Filtrar apenas as cidades com alertas
        return {city: data for city, data in alerts.items() if data}
    
    def generate_all_alerts(self):
        """
        Gera todos os alertas de temperatura e umidade.
        
        Returns:
            dict: Dicionário com todos os alertas por cidade e tipo
        """
        # Carregar dados se necessário
        if not self.meteogram_data:
            self.load_meteogram_data()
            if not self.meteogram_data:
                return {}
        
        # Obter alertas de temperatura
        temp_alerts = self.check_temperature_alerts()
        
        # Obter alertas de umidade
        humidity_alerts = self.check_humidity_alerts()
        
        # Combinar os alertas
        all_alerts = {}
        
        # Adicionar alertas de temperatura
        for city, alerts in temp_alerts.items():
            if city not in all_alerts:
                all_alerts[city] = {}
            all_alerts[city].update(alerts)
        
        # Adicionar alertas de umidade
        for city, alerts in humidity_alerts.items():
            if city not in all_alerts:
                all_alerts[city] = {}
            all_alerts[city].update(alerts)
        
        # Armazenar os alertas gerados
        self.alerts = all_alerts
        
        return all_alerts
    
    def send_email_alerts(self):
        """
        Envia alertas por email para os destinatários especificados.
        Se nenhum destinatário for fornecido, busca os destinatários usando o AlertService.
        
        Args:
            email_recipients (list, optional): Lista de endereços de email
        
        Returns:
            int: Número de alertas enviados
        """
        if not self.alerts:
            self.generate_all_alerts()
            if not self.alerts:
                print("Nenhum alerta para enviar")
                return 0
        
        alerts_sent = 0
        
        for city, city_alerts in self.alerts.items():
            # Alerta de temperatura alta
            if 'temperature_high' in city_alerts:
                alert = city_alerts['temperature_high']
                alert_date = self.get_alert_date(alert['seconds'])
                subject = f"AVISO: Previsão de temperaturas elevadas em {city} para o dia {alert_date}"
                
                if self.alert_service:
                    try:
                        users = self.alert_service.get_users_by_alert_and_city(
                            alert_types=["Temperatura"],
                            cities=[city]
                        )
                        for user in users:
                            try:
                                start_time = self.seconds_to_hhmm(alert['seconds'] - 3600)
                                end_time = self.seconds_to_hhmm(alert['seconds'] + 3600)
                                
                                content = self.content_strategy.generate_temperature_content(
                                    cidade_nome=city,
                                    valor=alert['value'],
                                    threshold=alert['threshold'],
                                    unit="°C",
                                    user_email=user.email,
                                    is_max=True,
                                    start_hour=start_time['formatted'],
                                    end_hour=end_time['formatted'],
                                    data=alert_date
                                )
                                
                                self.email_sender.send([user.email], content, subject)
                                alerts_sent += 1
                            except Exception as e:
                                print(f"Erro ao enviar email de alerta de temperatura alta para {user.email} em {city}: {str(e)}")
                                continue
                    except Exception as e:
                        print(f"Erro ao buscar destinatários para {city}: {str(e)}")
                        continue
                
                if not users:
                    print(f"Nenhum destinatário encontrado para alerta de temperatura alta em {city}")
                    continue

            # Alerta de temperatura baixa
            if 'temperature_low' in city_alerts:
                alert = city_alerts['temperature_low']
                alert_date = self.get_alert_date(alert['seconds'])
                subject = f"AVISO: Previsão de temperaturas baixas em {city} para o dia {alert_date}"
                
                if self.alert_service:
                    try:
                        users = self.alert_service.get_users_by_alert_and_city(
                            alert_types=["Temperatura"],
                            cities=[city]
                        )
                        for user in users:
                            try:
                                start_time = self.seconds_to_hhmm(alert['seconds'] - 3600)
                                end_time = self.seconds_to_hhmm(alert['seconds'] + 3600)
                                
                                content = self.content_strategy.generate_temperature_content(
                                    cidade_nome=city,
                                    valor=alert['value'],
                                    threshold=alert['threshold'],
                                    unit="°C",
                                    user_email=user.email,
                                    is_max=False,
                                    start_hour=start_time['formatted'],
                                    end_hour=end_time['formatted'],
                                    data=alert_date
                                )
                                
                                self.email_sender.send([user.email], content, subject)
                                alerts_sent += 1
                            except Exception as e:
                                print(f"Erro ao enviar email de alerta de temperatura baixa para {user.email} em {city}: {str(e)}")
                                continue
                    except Exception as e:
                        print(f"Erro ao buscar destinatários para {city}: {str(e)}")
                        continue
                
                if not users:
                    print(f"Nenhum destinatário encontrado para alerta de temperatura baixa em {city}")
                    continue

            # Alerta de umidade baixa
            if 'humidity_low' in city_alerts:
                alert = city_alerts['humidity_low']
                alert_date = self.get_alert_date(alert['seconds'])
                subject = f"AVISO: Previsão de baixa umidade relativa do ar em {city} para o dia {alert_date}"
                
                if self.alert_service:
                    try:
                        users = self.alert_service.get_users_by_alert_and_city(
                            alert_types=["Umidade"],
                            cities=[city]
                        )
                        for user in users:
                            try:
                                start_time = self.seconds_to_hhmm(alert['seconds'] - 3600)
                                end_time = self.seconds_to_hhmm(alert['seconds'] + 3600)
                                
                                content = self.content_strategy.generate_humidity_content(
                                    cidade_nome=city,
                                    valor=alert['value'],
                                    threshold=alert['threshold'],
                                    unit="%",
                                    user_email=user.email,
                                    is_max=False,
                                    start_hour=start_time['formatted'],
                                    end_hour=end_time['formatted'],
                                    data=alert_date
                                )
                                
                                self.email_sender.send([user.email], content, subject)
                                alerts_sent += 1
                            except Exception as e:
                                print(f"Erro ao enviar email de alerta de umidade baixa para {user.email} em {city}: {str(e)}")
                                continue
                    except Exception as e:
                        print(f"Erro ao buscar destinatários para {city}: {str(e)}")
                        continue
                
                if not users:
                    print(f"Nenhum destinatário encontrado para alerta de umidade baixa em {city}")
                    continue
                
        return alerts_sent
    
    def get_alert_date(self, seconds):
        """
        Obtém a data completa do alerta baseada nos segundos.
        
        Args:
            seconds (int): Segundos desde meia-noite em UTC-0
            
        Returns:
            str: Data formatada como "DD/MM/YYYY"
        """
        time_info = self.seconds_to_hhmm(seconds)
        today = datetime.now()
        
        # Usar o dia calculado pela função seconds_to_hhmm
        alert_day = time_info['day']
        
        # Criar a data usando o dia calculado e o mês/ano atuais
        alert_date = today.replace(day=alert_day)
        
        return alert_date.strftime('%d/%m/%Y')

    def get_alerts_summary(self):
        """
        Retorna um resumo dos alertas gerados.
        
        Returns:
            str: Resumo formatado dos alertas
        """
        if not self.alerts:
            return "Nenhum alerta gerado"
        
        summary = "=== RESUMO DE ALERTAS ===\n"
        
        for city, city_alerts in self.alerts.items():
            summary += f"\nCidade: {city}\n"
            
            if 'temperature_high' in city_alerts:
                alert = city_alerts['temperature_high']
                temp_k = alert.get('value_k', 'N/A')
                
                if isinstance(temp_k, (int, float)):
                    summary += f"  - Temperatura alta: {alert['value']:.1f}°C ({temp_k:.1f}K)\n"
                else:
                    summary += f"  - Temperatura alta: {alert['value']:.1f}°C\n"
                    
                summary += f"    Limite: {alert['threshold']}°C\n"
                summary += f"    Diferença: {alert['difference']:.1f}°C\n"
                summary += f"    Segundos: {alert['seconds']}\n"
                summary += f"    Data: {self.get_alert_date(alert['seconds'])}\n"
                summary += f"    Horário: {self.seconds_to_hhmm(alert['seconds'])['formatted']}\n"
            
            if 'temperature_low' in city_alerts:
                alert = city_alerts['temperature_low']
                temp_k = alert.get('value_k', 'N/A')
                
                if isinstance(temp_k, (int, float)):
                    summary += f"  - Temperatura baixa: {alert['value']:.1f}°C ({temp_k:.1f}K)\n"
                else:
                    summary += f"  - Temperatura baixa: {alert['value']:.1f}°C\n"
                    
                summary += f"    Limite: {alert['threshold']}°C\n"
                summary += f"    Diferença: {alert['difference']:.1f}°C\n"
                summary += f"    Segundos: {alert['seconds']}\n"
                summary += f"    Data: {self.get_alert_date(alert['seconds'])}\n"
                summary += f"    Horário: {self.seconds_to_hhmm(alert['seconds'])['formatted']}\n"
            
            if 'humidity_low' in city_alerts:
                alert = city_alerts['humidity_low']
                summary += f"  - Umidade baixa: {alert['value']:.1f}% (limite: {alert['threshold']}%)\n"
                summary += f"    Diferença: {alert['difference']:.1f}%\n"
                
                # Adicionar informações de temperatura se disponíveis
                if 'tave' in alert and 'tdave' in alert:
                    summary += f"    Temperatura média (Tave): {alert['tave']:.1f}°C\n"
                    summary += f"    Temperatura ponto de orvalho (TDave): {alert['tdave']:.1f}°C\n"
                
                summary += f"    Segundos: {alert['seconds']}\n"
                summary += f"    Data: {self.get_alert_date(alert['seconds'])}\n"
                summary += f"    Horário: {self.seconds_to_hhmm(alert['seconds'])['formatted']}\n"
        
        return summary

    def seconds_to_hhmm(self, seconds):
        """
        Converte segundos para componentes de tempo (horas, minutos e dia), ajustando de UTC-0 para UTC-3.
        Calcula automaticamente o dia correto quando o horário cruza meia-noite.
        
        Args:
            seconds (int): Segundos desde meia-noite em UTC-0
            
        Returns:
            dict: Dicionário com componentes de tempo em UTC-3:
                {
                    'hours': int,      # Horas (0-23)
                    'minutes': int,    # Minutos (0-59)
                    'day': int,        # Dia do mês (1-31)
                    'formatted': str   # String formatada como "DD HH:MM"
                }
        """
        # Converter para inteiro antes de calcular horas e minutos
        seconds = int(seconds)
        
        # Converter de UTC-0 para UTC-3 (subtrair 3 horas = 10800 segundos)
        seconds_utc3 = seconds - 10800
        
        # Usar a data de hoje como base
        today = datetime.now()
        
        # Calcular o dia baseado no horário resultante
        if seconds_utc3 < 0:
            # Se cruza meia-noite (segundos_utc3 < 0), usar o dia anterior
            from datetime import timedelta
            previous_day = today - timedelta(days=1)
            day = previous_day.day
            seconds_utc3 += 86400  # Adicionar 24 horas (86400 segundos)
        elif seconds_utc3 >= 86400:
            # Se ultrapassa 24 horas (86400 segundos), usar o próximo dia
            from datetime import timedelta
            next_day = today + timedelta(days=1)
            day = next_day.day
            seconds_utc3 -= 86400  # Subtrair 24 horas (86400 segundos)
        else:
            # Dentro do mesmo dia
            day = today.day
        
        # Calcular horas e minutos
        hours = seconds_utc3 // 3600
        minutes = (seconds_utc3 % 3600) // 60
        
        return {
            'hours': hours,
            'minutes': minutes,
            'day': day,
            'formatted': f"{hours:02d}:{minutes:02d}"
        }

    def create_control_file(self, meteogram_filename, error=None):
        """
        Cria um arquivo de controle para indicar que o processamento do dia foi concluído.
        
        Args:
            meteogram_filename (str): Nome do arquivo de meteograma processado
            error (str, optional): Mensagem de erro associada ao processamento
            
        Returns:
            str: Caminho do arquivo de controle criado
        """
        # Obter o diretório do arquivo de meteograma
        meteogram_dir = os.path.dirname(self.meteogram_path)
        
        # Criar nome do arquivo de controle (adicionar .processed ao nome original)
        control_filename = f"{os.path.splitext(meteogram_filename)[0]}.processed"
        control_path = os.path.join(meteogram_dir, control_filename)
        
        # Criar arquivo de controle com timestamp e mensagem de erro
        with open(control_path, 'w') as f:
            f.write(f"Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Arquivo original: {meteogram_filename}\n")
            if error:
                f.write(f"Erro: {error}\n")
        
        print(f"Arquivo de controle criado: {control_path}")
        return control_path

if __name__ == "__main__":
    import time
    start_time = time.time()
    
    # Obter o diretório atual onde o script está sendo executado
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Caminho para o arquivo de configuração (2 níveis acima da pasta src)
    config_path = os.path.abspath(os.path.join(current_dir, '../../', 'config.csv'))
    
    print(f"Usando arquivo de configuração: {config_path}")

    # Gerar o nome do arquivo de meteograma com base na data atual
    today = datetime.now()
    meteogram_filename = f"HST{today.year}{today.month:02d}{today.day:02d}00-MeteogramASC.out"
    
    meteogramPathDir = os.path.abspath(os.path.join(current_dir, '../../', 'tmp_files'))
    meteogramPath = os.path.join(meteogramPathDir, meteogram_filename)
    
    # Verificar se já existe arquivo de controle para este dia
    control_filename = f"{os.path.splitext(meteogram_filename)[0]}.processed"
    control_path = os.path.join(meteogramPathDir, control_filename)
    
    if os.path.exists(control_path):
        print(f"Arquivo de controle encontrado: {control_path}")
        print("Este arquivo já foi processado hoje. Encerrando execução.")
        sys.exit(0)
    
    print(f"Buscando arquivo de meteograma: {meteogramPath}")

    # Limpar arquivos antigos
    clean_old_files(meteogramPathDir)
    
    # Baixar o arquivo de meteograma mais recente
    downloaded_path = download_meteogram_file(
        date=f"{today.year}{today.month:02d}{today.day:02d}",
        directory=meteogramPathDir
    )
    
    if not downloaded_path:
        print("ERRO: Não foi possível baixar o arquivo de meteograma")
        sys.exit(1)
    
    # Criar contexto de aplicação para usar o serviço
    app = create_app()
    
    with app.app_context():
        try:
            alert_gen = AlertGenerator(
                config_path=config_path,
                meteogram_path=downloaded_path,  # Usar o caminho do arquivo baixado
                alert_service=AlertService
                )
            
            # Carregar dados meteorológicos
            data = alert_gen.load_meteogram_data()
            
            if data:
                # Verificar alertas
                alerts = alert_gen.generate_all_alerts()
                
                # Mostrar resumo
                print(alert_gen.get_alerts_summary())
                
                # Enviar alertas
                if alerts:
                    alerts_enviados = alert_gen.send_email_alerts()
                    print(f"Enviados {alerts_enviados} alertas para os destinatários cadastrados")
                
                # Criar arquivo de controle para indicar que o processamento foi concluído com sucesso
                alert_gen.create_control_file(meteogram_filename)
                print("Processamento concluído com sucesso!")
            else:
                error_msg = "Não foi possível carregar os dados do meteograma"
                print(error_msg)
                # Criar arquivo de controle com erro
                alert_gen.create_control_file(meteogram_filename, error=error_msg)
                
        except FileNotFoundError as e:
            error_msg = f"ERRO FATAL: {str(e)} - Não foi possível continuar o processamento. Verifique o arquivo de configuração."
            print(error_msg)
            # Criar arquivo de controle com erro
            alert_gen.create_control_file(meteogram_filename, error=error_msg)
            sys.exit(1)
        except Exception as e:
            error_msg = f"ERRO FATAL: {str(e)} - Ocorreu um erro inesperado durante o processamento."
            print(error_msg)
            # Criar arquivo de controle com erro
            alert_gen.create_control_file(meteogram_filename, error=error_msg)
            sys.exit(1)
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"\nTempo total de execução: {execution_time:.2f} segundos")
