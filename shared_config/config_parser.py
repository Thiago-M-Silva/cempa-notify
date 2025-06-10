import os
import pandas as pd

class ConfigParser:
    """
    Classe para carregar e gerenciar configurações a partir de arquivos CSV.
    Fornece métodos para acessar limiares de temperatura e outras informações.
    """
    
    def __init__(self, config_path=None):
        """
        Inicializa o parser de configuração.
        
        Args:
            config_path (str, optional): Caminho para o arquivo de configuração.
                Se None, usa o caminho padrão relativo ao diretório atual.
                
        Raises:
            FileNotFoundError: Se o arquivo de configuração não for encontrado
            ValueError: Se o caminho do arquivo não for fornecido
        """
        self.config_map = {}
        self.config_path = config_path
        
        # Verificar se o caminho foi fornecido
        if self.config_path is None:
            raise ValueError("Caminho do arquivo de configuração não fornecido")
        
        # Verificar se o arquivo existe
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")
    
    def parse(self):
        """
        Carrega o arquivo config_files.csv e transforma em um dicionário
        onde a chave é o polygon_name.
        
        Returns:
            self: Para permitir chamadas encadeadas
            
        Raises:
            Exception: Se ocorrer erro ao processar o arquivo
        """
        try:
            # Ler o CSV de configuração
            config_df = pd.read_csv(self.config_path)
            
            # Transformar o DataFrame em um dicionário
            self.config_map = {}
            
            for _, row in config_df.iterrows():
                polygon_name = row['polygon_name_meteogram']
                
                # Criar dicionário com os valores da linha
                polygon_config = row.to_dict()
                
                # Adicionar ao mapa
                self.config_map[polygon_name] = polygon_config
            
            if not self.config_map:
                raise ValueError(f"Nenhuma configuração encontrada no arquivo: {self.config_path}")
                
            return self
            
        except Exception as e:
            error_msg = f"Erro ao processar arquivo de configuração: {str(e)}"
            print(error_msg)
            raise Exception(error_msg) from e
    
    def get_config_map(self):
        """
        Retorna o mapa de configuração completo.
        
        Returns:
            dict: Dicionário com configurações por polígono
        """
        # Se o mapa estiver vazio, tenta carregar
        if not self.config_map:
            self.parse()
        return self.config_map
    
    def get_monthly_temp_threshold(self, polygon_name, month, threshold_type='max'):
        """
        Obtém o limite de temperatura para um mês específico.
        
        Args:
            polygon_name (str): Nome do polígono
            month (int): Mês (1-12)
            threshold_type (str): Tipo de limite ('max' ou 'min')
            
        Returns:
            float: Valor do limite ou None se não encontrado
        """
        # Se o mapa estiver vazio, tenta carregar
        if not self.config_map:
            self.parse()
            
        if polygon_name not in self.config_map:
            return None
        
        month_names = {
            1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
            7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"
        }
        
        if month not in month_names:
            return None
            
        month_name = month_names[month]
        key = f"temp_{threshold_type}_{month_name}"
        
        return self.config_map[polygon_name].get(key)
    
    def get_display_name(self, polygon_name):
        """
        Obtém o nome de exibição para um polígono.
        
        Args:
            polygon_name (str): Nome do polígono
            
        Returns:
            str: Nome de exibição ou None se não encontrado
        """
        # Se o mapa estiver vazio, tenta carregar
        if not self.config_map:
            self.parse()
            
        if polygon_name not in self.config_map:
            return None
            
        return self.config_map[polygon_name].get('display_name')
    
    def get_polygons(self):
        """
        Retorna a lista de nomes de polígonos disponíveis.
        
        Returns:
            list: Lista de nomes de polígonos
        """
        # Se o mapa estiver vazio, tenta carregar
        if not self.config_map:
            self.parse()
            
        return list(self.config_map.keys())
    
    def get_polygon_config(self, polygon_name):
        """
        Retorna a configuração completa de um polígono.
        
        Args:
            polygon_name (str): Nome do polígono
            
        Returns:
            dict: Configuração do polígono ou None se não encontrado
        """
        # Se o mapa estiver vazio, tenta carregar
        if not self.config_map:
            self.parse()
            
        return self.config_map.get(polygon_name)
