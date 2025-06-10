import os
import pandas as pd
from datetime import datetime
from config_parser import load_config_as_map, get_monthly_temp_threshold, get_display_name

def validate_max_temperature(polygon_name, temperature, date=None, config_map=None):
    """
    Valida se a temperatura máxima está dentro dos limites estabelecidos para o polígono no mês correspondente.
    
    Args:
        polygon_name (str): Nome do polígono (ex: "5730-RMG-Regiao_Metropolitana_de_Goiania - GO")
        temperature (float): Temperatura máxima a ser validada
        date (datetime, optional): Data para determinar o mês. Se None, usa a data atual.
        config_map (dict, optional): Mapa de configuração pré-carregado. Se None, carrega do arquivo.
    
    Returns:
        dict: Dicionário com resultados da validação:
            - valid (bool): Se a temperatura está dentro do limite
            - threshold (float): Limite máximo para o mês
            - difference (float): Diferença entre temperatura e limite (positivo se ultrapassou)
            - month (int): Mês utilizado para validação
            - polygon_name (str): Nome do polígono validado
            - display_name (str): Nome de exibição do polígono
    """
    # Determinar o mês atual se não for fornecido
    if date is None:
        date = datetime.now()
    
    month = date.month
    
    # Carregar o mapa de configuração se não foi fornecido
    if config_map is None:
        config_map = load_config_as_map()
    
    try:
        # Verificar se o polígono existe na configuração
        if polygon_name not in config_map:
            return {
                "valid": False,
                "error": f"Polígono '{polygon_name}' não encontrado no arquivo de configuração",
                "threshold": None,
                "difference": None,
                "month": month,
                "polygon_name": polygon_name,
                "display_name": None
            }
        
        # Obter o limite para o mês específico
        max_threshold = get_monthly_temp_threshold(config_map, polygon_name, month, 'max')
        
        if max_threshold is None:
            return {
                "valid": False,
                "error": f"Limite de temperatura máxima não encontrado para o mês {month}",
                "threshold": None,
                "difference": None,
                "month": month,
                "polygon_name": polygon_name,
                "display_name": get_display_name(config_map, polygon_name)
            }
        
        # Validar a temperatura
        is_valid = temperature <= max_threshold
        difference = temperature - max_threshold
        
        return {
            "valid": is_valid,
            "threshold": max_threshold,
            "difference": difference,
            "month": month,
            "polygon_name": polygon_name,
            "display_name": get_display_name(config_map, polygon_name)
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Erro ao validar temperatura: {str(e)}",
            "threshold": None,
            "difference": None,
            "month": month,
            "polygon_name": polygon_name,
            "display_name": get_display_name(config_map, polygon_name) if config_map and polygon_name in config_map else None
        }


def validate_meteogram_data(data, date=None):
    """
    Valida os dados do meteograma para todos os polígonos retornados.
    
    Args:
        data (dict): Dados retornados pelo MeteogramParser.parse()
        date (datetime, optional): Data para determinar o mês. Se None, usa a data atual.
    
    Returns:
        dict: Dicionário com resultados da validação por polígono
    """
    results = {}
    
    # Carregar o mapa de configuração uma única vez para eficiência
    config_map = load_config_as_map()
    
    for polygon_name, time_data in data.items():
        # Para cada tempo nos dados do polígono
        polygon_results = []
        
        for seconds, values in time_data.items():
            # Verificar se temos a coluna 'TEMP'
            if 'TEMP' in values:
                temperature = values['TEMP']
                validation = validate_max_temperature(polygon_name, temperature, date, config_map)
                
                # Adicionar informações de tempo aos resultados
                validation['seconds'] = seconds
                if 'date' in values:
                    validation['date'] = values['date']
                
                polygon_results.append(validation)
        
        # Armazenar os resultados para este polígono
        if polygon_results:
            results[polygon_name] = polygon_results
    
    return results 