import os
import pandas as pd

class MeteogramParser:
    """
    Parser para extrair dados de arquivos de meteogramas com padrão "nCities: 1922".
    
    Este parser lê arquivos de saída do tipo 'HST*-MeteogramASC.out' que contêm 
    dados meteorológicos para várias cidades, extraindo os dados em formato tabular.
    """
    
    def __init__(self, file_path=None):
        """
        Inicializa o parser com um arquivo.
        
        Args:
            file_path (str, optional): Caminho para o arquivo a ser processado
            
        Raises:
            ValueError: Se o caminho do arquivo não for fornecido
            FileNotFoundError: Se o arquivo não for encontrado
        """
        if file_path is None:
            raise ValueError("Caminho do arquivo de meteograma não fornecido")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo de meteograma não encontrado: {file_path}")
        
        self.file_path = file_path
        self.city_data = {}
        self.city_count = 0
        self.headers = []
        self.dates = []
        self.seconds = []
        self.current_seconds = None
    
    def set_file(self, file_path):
        """
        Define o arquivo a ser processado.
        
        Args:
            file_path (str): Caminho para o arquivo a ser processado
            
        Returns:
            self: Para chamadas encadeadas
            
        Raises:
            ValueError: Se o caminho do arquivo não for fornecido
            FileNotFoundError: Se o arquivo não for encontrado
        """
        if file_path is None:
            raise ValueError("Caminho do arquivo de meteograma não fornecido")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo de meteograma não encontrado: {file_path}")
        
        self.file_path = file_path
        return self
    
    def parse(self, max_seconds=86400, filter_state="GO"):
        """
        Processa o arquivo e extrai os dados.
        
        Args:
            max_seconds (int): Valor máximo de segundos para processar (padrão: 86400, um dia)
            filter_state (str, optional): Filtrar apenas polígonos deste estado. Se None, não filtra por estado.
            
        Returns:
            dict: Dicionário com os dados extraídos por cidade e segundos
                 Formato: {polygon_name: {segundos: {coluna: valor, ...}}}
                 
        Raises:
            Exception: Se ocorrer erro ao processar o arquivo
        """
        # Inicializar dicionários e listas para armazenar os dados
        self.city_data = {}
        self.headers = []
        self.dates = []
        self.seconds = []
        self.current_seconds = None
        
        # Contadores para estatísticas
        total_polygons = 0
        filtered_polygons = 0
        
        # Lê o arquivo em blocos para economizar memória
        with open(self.file_path, 'r', encoding='utf-8') as f:
            # Ler o arquivo linha por linha
            line_num = 0
            current_city = None
            current_data = []
            
            while True:
                line = f.readline()
                if not line:
                    break
                
                line_num += 1
                line = line.strip()
                
                # Verificar se a linha contém um cabeçalho de tempo
                # Formato: '394200.000            2025           4          29           0'
                if line and line[0].isdigit() and len(line.split()) >= 5:
                    parts = line.split()
                    try:
                        seconds = float(parts[0])
                        year = int(parts[1])
                        month = int(parts[2])
                        day = int(parts[3])
                        hour = int(parts[4])
                        
                        # Armazenar os dados de tempo
                        self.seconds.append(seconds)
                        self.dates.append(f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:00:00")
                        
                        # Atualizar os segundos atuais
                        self.current_seconds = seconds
                        
                        # Se ultrapassou o limite de segundos (um dia), para o processamento
                        if seconds > max_seconds:
                            print(f"Atingido limite de segundos ({max_seconds}). Parando o processamento.")
                            break
                        
                        # Ler a próxima linha que deve ser o cabeçalho das colunas
                        header_line = f.readline().strip()
                        self.headers = header_line.split()
                        
                        # Continuar para a próxima linha
                        continue
                    except (ValueError, IndexError):
                        # Não é um cabeçalho de tempo, continua normalmente
                        pass
                
                # Detectar o cabeçalho "nCities"
                if line.startswith("nCities:"):
                    # Extrair o número de cidades
                    parts = line.split()
                    if len(parts) >= 2:
                        self.city_count = int(parts[1])
                    
                    # Continuar, pois a próxima linha deve ser o timestamp
                    continue
                
                # Processar linhas de dados (cidades)
                # Verificar se é uma linha de dados de cidade
                if line and not line.startswith("nCities:") and len(line.split()) > 3 and self.current_seconds is not None:
                    total_polygons += 1
                    
                    # Primeiro campo contém o nome do polígono - Formato: 5730-RMG-Regiao_Metropolitana_de_Goiania - GO
                    parts = line.split()

                    if len(parts) < 3:
                        continue

                    if parts[2] != filter_state:
                        continue

                    polygon_name = parts[0]
                        
                    if polygon_name:
                        # Extrair valores numéricos
                        city_values = []
                        for val in parts:
                            try:
                                city_values.append(float(val))
                            except ValueError:
                                city_values.append(val)
                        
                        # Inicializar estrutura para a cidade se necessário
                        if polygon_name not in self.city_data:
                            self.city_data[polygon_name] = {}
                        
                        # Inicializar estrutura para os segundos desta cidade
                        if self.current_seconds not in self.city_data[polygon_name]:
                            self.city_data[polygon_name][self.current_seconds] = {}
                        
                        # Criar dicionário com pares de cabeçalho:valor
                        city_entry = {}
                        for i, header in enumerate(self.headers):
                            if i < len(city_values):
                                city_entry[header] = city_values[i]
                        
                        # Adicionar informação de tempo
                        city_entry['seconds'] = self.current_seconds
                        current_date_idx = self.seconds.index(self.current_seconds) if self.current_seconds in self.seconds else -1
                        if current_date_idx >= 0 and current_date_idx < len(self.dates):
                            city_entry['date'] = self.dates[current_date_idx]
                        
                        # Armazenar dados na estrutura principal
                        self.city_data[polygon_name][self.current_seconds] = city_entry
        
        # Exibir estatísticas do parsing
        total_timestamps = len(self.seconds)
        if total_timestamps > 0:
            print(f"Intervalo de tempo: {self.seconds[0]} a {self.seconds[-1]} segundos")
        
        if filter_state:
            print(f"Total de polígonos encontrados: {total_polygons}")
            print(f"Polígonos de {filter_state} mantidos: {filtered_polygons}")
            print(f"Polígonos filtrados: {total_polygons - filtered_polygons}")
        
        return self.city_data
    
    def get_polygon_names(self):
        """
        Retorna a lista de nomes de polígonos encontrados no arquivo.
        
        Returns:
            list: Lista de nomes de polígonos
        """
        if not self.city_data:
            self.parse()
        
        return list(self.city_data.keys())
    
    def get_headers(self):
        """
        Retorna os cabeçalhos das colunas encontradas no arquivo.
        
        Returns:
            list: Lista de cabeçalhos
        """
        if not self.headers and self.file_path:
            self.parse()
        
        return self.headers
    
    def get_timestamps(self):
        """
        Retorna a lista de timestamps (segundos) encontrados no arquivo.
        
        Returns:
            list: Lista de valores de segundos
        """
        if not self.seconds and self.file_path:
            self.parse()
        
        return self.seconds
    
    def get_dates(self):
        """
        Retorna a lista de datas encontradas no arquivo.
        
        Returns:
            list: Lista de datas formatadas
        """
        if not self.dates and self.file_path:
            self.parse()
        
        return self.dates
    
    @staticmethod
    def find_meteogram_files(directory):
        """
        Encontra todos os arquivos de meteograma em um diretório.
        
        Args:
            directory (str): Diretório a ser pesquisado
            
        Returns:
            list: Lista de caminhos para arquivos de meteograma
        """
        meteogram_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith("-MeteogramASC.out"):
                    meteogram_files.append(os.path.join(root, file))
        
        return meteogram_files
