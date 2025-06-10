import os
import pandas as pd
from datetime import datetime
from meteogram_parser import MeteogramParser
from sendEmail import EmailSender
from generateMail import generate_temperature_alert_email, generate_humidity_alert_email
from file_utils import clean_old_files
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from modulo_usuarios.src import create_app
from modulo_usuarios.src.services import AlertService
from shared_config.config_parser import ConfigParser

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
    
    def to_dataframe(self):
        """
        Converte os dados do meteograma para um DataFrame.
        
        Returns:
            pandas.DataFrame: DataFrame com os dados de todos os polígonos
        """
        if not self.meteogram_data:
            self.load_meteogram_data()
            if not self.meteogram_data:
                return pd.DataFrame()
        
        all_data = []
        
        for polygon_name, time_data in self.meteogram_data.items():
            display_name = self.config.get_display_name(polygon_name)
            
            for seconds, values in time_data.items():
                # Criar uma cópia do dicionário de valores
                row = values.copy()
                
                # Converter Tmax de Kelvin para Celsius se existir
                if 'Tmax' in row:
                    row['Tmax_K'] = row['Tmax']  # Preservar o valor original em Kelvin
                    row['Tmax'] = self.kelvin_to_celsius(row['Tmax'])  # Converter para Celsius
                
                # Adicionar informações do polígono
                row['polygon_name'] = polygon_name
                row['display_name'] = display_name
                row['seconds'] = seconds
                
                # Adicionar à lista de dados
                all_data.append(row)
        
        # Criar DataFrame
        df = pd.DataFrame(all_data)
        
        # Converter coluna 'date' para datetime se existir
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def check_temperature_alerts(self, date=None):
        """
        Verifica se há alertas de temperatura baseados nos limiares configurados.
        
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
            
            # Obter o limiar de temperatura para este mês
            threshold = self.config.get_monthly_temp_threshold(polygon_name, month)
            
            if not threshold:
                continue  # Pular se não tiver limiar configurado
            
            # Verificar se o polígono existe nos dados do meteograma
            if polygon_name not in self.meteogram_data:
                continue  # Pular se não tiver dados para este polígono
            
            time_data = self.meteogram_data[polygon_name]
            
            # Inicializar o alerta para esta cidade se ainda não existir
            if display_name not in alerts:
                alerts[display_name] = {}
            
            # Verificar cada registro de tempo
            max_temp_c = float('-inf')
            max_temp_data = None
            
            for seconds, values in time_data.items():
                if 'Tmax' in values:
                    # Converter de Kelvin para Celsius
                    temp_k = values['Tmax']
                    temp_c = self.kelvin_to_celsius(temp_k)
                    
                    # Atualizar a temperatura máxima (em Celsius)
                    if temp_c > max_temp_c:
                        max_temp_c = temp_c
                        max_temp_data = {
                            'polygon_name': polygon_name,
                            'seconds': seconds,
                            'date': values.get('date', 'N/A'),
                            'temp_k': temp_k,
                            'temp_c': temp_c,
                            'threshold': threshold,
                            'difference': temp_c - threshold
                        }
            
            # Se encontrou temperatura acima do limiar
            if max_temp_c > threshold and max_temp_data:
                # Armazenar o alerta para esta cidade
                alerts[display_name]['temperature'] = {
                    'value': max_temp_c,
                    'value_k': max_temp_data['temp_k'],
                    'threshold': threshold,
                    'difference': max_temp_c - threshold,
                    'date': max_temp_data['date'],
                    'seconds': max_temp_data['seconds'],
                    'polygon_name': polygon_name
                }
        
        # Filtrar apenas as cidades com alertas
        return {city: data for city, data in alerts.items() if data}
    
    def check_humidity_alerts(self, min_threshold=30, max_threshold=90, date=None):
        """
        Verifica se há alertas de umidade baseados nos limiares especificados.
        Gera alertas apenas para umidade baixa (abaixo do limiar mínimo).
        
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
                if 'UMRL' in values:  # Assumindo que UMRL é a coluna de umidade relativa
                    humidity = values['UMRL']
                    
                    # Atualizar a umidade mínima
                    if humidity < min_humidity:
                        min_humidity = humidity
                        min_humidity_data = {
                            'polygon_name': polygon_name,
                            'seconds': seconds,
                            'date': values.get('date', 'N/A'),
                            'humidity': humidity,
                            'threshold': min_threshold,
                            'difference': humidity - min_threshold
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
    
    def send_email_alerts(self, email_recipients=None):
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
            # Alerta de temperatura
            if 'temperature' in city_alerts:
                alert = city_alerts['temperature']
                subject = f"ALERTA: Temperatura acima do limite em {city}"
                
                # Buscar destinatários específicos para este alerta
                recipients = email_recipients
                if not recipients and self.alert_service:
                    try:
                        # Buscar usuários baseados na cidade e tipo de alerta
                        users = self.alert_service.get_users_by_alert_and_city(
                            alert_types=["Temperatura"],
                            cities=[city]  # Usar o nome de exibição da cidade diretamente
                        )
                        recipients = [user.email for user in users]
                        print(f"Encontrados {len(recipients)} destinatários para alerta de temperatura em {city}")
                    except Exception as e:
                        print(f"Erro ao buscar destinatários para {city}: {str(e)}")
                        continue
                
                if not recipients:
                    print(f"Nenhum destinatário encontrado para alerta de temperatura em {city}")
                    continue
                
                email_content = generate_temperature_alert_email(
                    city,
                    alert['value'],
                    alert['threshold'],
                    "°C",
                    f"Data/Hora: {alert['date']}",
                    True,
                    alert['difference']
                )
                
                try:
                    self.email_sender.enviar_email(recipients, email_content, subject)
                    print(f"Email de alerta de temperatura enviado para {city} ({len(recipients)} destinatários)")
                    alerts_sent += 1
                except Exception as e:
                    print(f"Erro ao enviar email de alerta de temperatura para {city}: {str(e)}")
            
            # Alerta de umidade baixa
            if 'humidity_low' in city_alerts:
                alert = city_alerts['humidity_low']
                subject = f"ALERTA: Umidade abaixo do limite em {city}"
                
                # Buscar destinatários específicos para este alerta
                recipients = email_recipients
                if not recipients and self.alert_service:
                    try:
                        # Buscar usuários baseados na cidade e tipo de alerta
                        users = self.alert_service.get_users_by_alert_and_city(
                            alert_types=["Umidade"],
                            cities=[city]  # Usar o nome de exibição da cidade diretamente
                        )
                        recipients = [user.email for user in users]
                        print(f"Encontrados {len(recipients)} destinatários para alerta de umidade baixa em {city}")
                    except Exception as e:
                        print(f"Erro ao buscar destinatários para {city}: {str(e)}")
                        continue
                
                if not recipients:
                    print(f"Nenhum destinatário encontrado para alerta de umidade baixa em {city}")
                    continue
                
                email_content = generate_humidity_alert_email(
                    city,
                    alert['value'],
                    alert['threshold'],
                    "%",
                    f"Data/Hora: {alert['date']}",
                    False
                )
                
                try:
                    self.email_sender.enviar_email(recipients, email_content, subject)
                    print(f"Email de alerta de umidade baixa enviado para {city} ({len(recipients)} destinatários)")
                    alerts_sent += 1
                except Exception as e:
                    print(f"Erro ao enviar email de alerta de umidade baixa para {city}: {str(e)}")
        
        return alerts_sent
    
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
            
            if 'temperature' in city_alerts:
                alert = city_alerts['temperature']
                temp_k = alert.get('value_k', 'N/A')
                
                if isinstance(temp_k, (int, float)):
                    summary += f"  - Temperatura: {alert['value']:.1f}°C ({temp_k:.1f}K)\n"
                else:
                    summary += f"  - Temperatura: {alert['value']:.1f}°C\n"
                    
                summary += f"    Limite: {alert['threshold']}°C\n"
                summary += f"    Diferença: {alert['difference']:.1f}°C\n"
                summary += f"    Data/Hora: {alert['date']}\n"
            
            if 'humidity_low' in city_alerts:
                alert = city_alerts['humidity_low']
                summary += f"  - Umidade baixa: {alert['value']:.1f}% (limite: {alert['threshold']}%)\n"
                summary += f"    Diferença: {alert['difference']:.1f}%\n"
                summary += f"    Data/Hora: {alert['date']}\n"
        
        return summary



forceDate = datetime(2025, 4, 29, 0, 0, 0)

if __name__ == "__main__":
    # Obter o diretório atual onde o script está sendo executado
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Caminho para o arquivo de configuração (2 níveis acima da pasta src)
    config_path = os.path.abspath(os.path.join(current_dir, '../../', 'config_files.csv'))
    
    print(f"Usando arquivo de configuração: {config_path}")

    # Gerar o nome do arquivo de meteograma com base na data atual
    today = forceDate if forceDate else datetime.now()
    meteogram_filename = f"HST{today.year}{today.month:02d}{today.day:02d}00-MeteogramASC.out"
    
    meteogramPathDir = os.path.abspath(os.path.join(current_dir, '../../', 'tmp_files'))
    meteogramPath = os.path.join(meteogramPathDir, meteogram_filename)
    
    print(f"Buscando arquivo de meteograma: {meteogramPath}")

    # Descomentar quando fazer deploy
    # clean_old_files(meteogramPathDir)
    
    # Criar contexto de aplicação para usar o serviço
    app = create_app()
    
    with app.app_context():
        print("Inicializando AlertGenerator com AlertService...")
        try:
            alert_gen = AlertGenerator(
                config_path=config_path,
                meteogram_path=meteogramPath,
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
            else:
                print("Não foi possível carregar os dados do meteograma")
                
            print("Processamento concluído com sucesso!")
        except FileNotFoundError as e:
            print(f"ERRO FATAL: {str(e)}")
            print("Não foi possível continuar o processamento. Verifique o arquivo de configuração.")
            sys.exit(1)
        except Exception as e:
            print(f"ERRO FATAL: {str(e)}")
            print("Ocorreu um erro inesperado durante o processamento.")
            sys.exit(1)
