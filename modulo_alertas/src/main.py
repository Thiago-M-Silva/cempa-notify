import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
import numpy as np
import subprocess
import pandas as pd
import os
import requests
from urllib.parse import urljoin
import datetime
import geopandas as gpd
from shapely.geometry import Point

CITIES = {
    "Goiânia": {
        "ibge_code": 5208707,
        "polygon": None,
        "alerts": {
            "temperature": {
                "max": 35,
                "min": 14
            },
            "umidade    ": {
                "max": 100,
                "min": 20
            }
        }
    },
    "Rio Verde": {
        "ibge_code": 5218805,
        "polygon": None,
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
    }
}

VARIABLES = {
    "temperature": {
        "unit": "°C",
        "brams_name": "t2mj",
    },
    "umidade": {
        "unit": "%",
        "brams_name": "rh",
    }
}

def download_file(url, local_filepath):
    """Baixa um arquivo de uma URL para um caminho local."""
    os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
    
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filepath

def download_cempa_files(date=None, hours=None):
    """
    Baixa arquivos CTL e GRA do servidor CEMPA para uma data específica.
    
    Args:
        date (str, optional): Data no formato YYYYMMDD. Se None, usa a data atual.
        hours (list, optional): Lista de horas para baixar (0-23). Se None, baixa todas as horas.
    """
    if date is None:
        date = datetime.datetime.now().strftime("%Y%m%d")
    
    if hours is None:
        hours = range(24)
    
    downloaded_files = []
    
    for hour in hours:
        hour_str = f"{hour:02d}"
        base_url = f"https://tatu.cempa.ufg.br/BRAMS-dataout/{date}00/"
        file_prefix = f"Go5km-A-{date[:4]}-{date[4:6]}-{date[6:8]}-{hour_str}0000-g1"
        
        ctl_url = urljoin(base_url, f"{file_prefix}.ctl")
        gra_url = urljoin(base_url, f"{file_prefix}.gra")
        
        files_dir = "./files"
        os.makedirs(files_dir, exist_ok=True)
        
        ctl_path = os.path.join(files_dir, f"{file_prefix}.ctl")
        gra_path = os.path.join(files_dir, f"{file_prefix}.gra")
        
        try:
            print(f"\nBaixando arquivos para hora {hour_str}:00...")
            print(f"Baixando {ctl_url}...")
            download_file(ctl_url, ctl_path)
            print(f"Baixando {gra_url}...")
            download_file(gra_url, gra_path)
            print(f"Downloads concluídos com sucesso para hora {hour_str}:00!")
            downloaded_files.append((ctl_path, gra_path))
        except requests.RequestException as e:
            print(f"Erro ao baixar arquivos para hora {hour_str}:00: {e}")
            continue
    
    if downloaded_files:
        print(f"\nTotal de arquivos baixados com sucesso: {len(downloaded_files)}")
        return downloaded_files
    else:
        print("\nNenhum arquivo foi baixado com sucesso.")
        return None


def convert_to_netcdf(ctl_path, output_nc):
    """Converte CTL/GRA para NetCDF usando CDO."""
    comando = [
        "cdo", "-f", "nc", "import_binary", ctl_path, output_nc
    ]

    try:
        subprocess.run(comando, check=True)
        print("Conversão concluída com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e}")
        return False

def plot_temperature(nc_file, date, output_image=None):
    """
    Cria um plot de temperatura a partir dos dados NetCDF.
    
    Args:
        nc_file (str): Caminho do arquivo NetCDF
        date (str): Data no formato YYYYMMDD00
        output_image (str, optional): Caminho para salvar a imagem. Se None, mostra o plot.
    """
    ds = xr.open_dataset(nc_file) 
    data = ds['rh'].isel(time=0)

    colors = [
        '#0000b2', '#005ce6', '#008c8c', '#008000', 
        '#66b032', '#ffff00', '#ffaa00', '#ff5500', 
        '#cc0000', '#7f0000'
    ]
    cmap = mcolors.LinearSegmentedColormap.from_list("cempa_like", colors, N=256)

    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Usar contourf ao invés de plot para suportar cmap
    contour = ax.contourf(
        data.lon,
        data.lat,
        data,
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        levels=np.arange(14, 39, 1),
        extend='both'
    )

    # Adicionar barra de cores
    cbar = plt.colorbar(contour, ax=ax, label='Temperatura [°C]')
    
    # Adicionar elementos do mapa
    ax.add_feature(cfeature.BORDERS, linewidth=1)
    ax.add_feature(cfeature.COASTLINE, linewidth=1)
    ax.add_feature(cfeature.STATES, linewidth=1)
    ax.add_feature(cfeature.LAND, linewidth=1)
    ax.set_extent([-54, -43, -21, -8.5]) 

    # Formatar a data para exibição
    date_formatted = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
    
    plt.title(f"Temperatura 2m para 00z {date_formatted}", fontsize=14)
    plt.suptitle(f"CEMPA/UFG - Previsão BRAMS iniciada em: 00z {date_formatted}", fontsize=12, color='steelblue')
    plt.tight_layout()
    
    if output_image:
        plt.savefig(output_image, dpi=300, bbox_inches='tight')
        print(f"Imagem salva em: {output_image}")
    else:
        plt.show()
    plt.close()

def plot_humidity(nc_file, date, output_image=None):
    """
    Cria um plot de umidade relativa a partir dos dados NetCDF.
    
    Args:
        nc_file (str): Caminho do arquivo NetCDF
        date (str): Data no formato YYYYMMDD00
        output_image (str, optional): Caminho para salvar a imagem. Se None, mostra o plot.
    """
    ds = xr.open_dataset(nc_file)
    
    # Selecionar o primeiro timestep e garantir que temos uma matriz 2D
    data = ds['rh'].isel(time=0)
    
    # Verificar e imprimir as dimensões para debug
    print(f"Dimensões dos dados: {data.dims}")
    print(f"Forma dos dados: {data.shape}")
    
    # Garantir que temos uma matriz 2D (lat, lon)
    if len(data.dims) > 2:
        # Usar lev_2 que é a dimensão correta
        data = data.isel(lev_2=0)
    
    # Cores para umidade relativa (do seco ao úmido)
    colors = [
        '#ffff00', '#ffcc00', '#ff9900', '#ff6600',  # Tons de amarelo/laranja para valores baixos
        '#00cc00', '#009900', '#006600', '#003300',  # Tons de verde para valores médios
        '#0000ff', '#000099', '#000066'              # Tons de azul para valores altos
    ]
    cmap = mcolors.LinearSegmentedColormap.from_list("humidity_colors", colors, N=256)

    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Usar contourf com níveis apropriados para umidade relativa
    contour = ax.contourf(
        data.lon,
        data.lat,
        data.values,  # Agora data.values já deve ser 2D
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        levels=np.arange(0, 101, 5),  # Umidade relativa de 0 a 100% em intervalos de 5%
        extend='both'
    )

    # Adicionar barra de cores
    cbar = plt.colorbar(contour, ax=ax, label='Umidade Relativa [%]')
    
    # Adicionar elementos do mapa
    ax.add_feature(cfeature.BORDERS, linewidth=1)
    ax.add_feature(cfeature.COASTLINE, linewidth=1)
    ax.add_feature(cfeature.STATES, linewidth=1)
    ax.add_feature(cfeature.LAND, linewidth=1)
    ax.set_extent([-54, -43, -21, -8.5]) 

    # Formatar a data para exibição
    date_formatted = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
    
    plt.title(f"Umidade Relativa para 00z {date_formatted}", fontsize=14)
    plt.suptitle(f"CEMPA/UFG - Previsão BRAMS iniciada em: 00z {date_formatted}", fontsize=12, color='steelblue')
    plt.tight_layout()
    
    if output_image:
        plt.savefig(output_image, dpi=300, bbox_inches='tight')
        print(f"Imagem salva em: {output_image}")
    else:
        plt.show()
    plt.close()

def find_extreme_variables(nc_file, municipio_info, var_types=None, max_distance_km=50):
    """
    Encontra os valores máximos e mínimos de múltiplas variáveis dentro dos limites do município.
    
    Args:
        nc_file (str): Caminho do arquivo NetCDF
        municipio_info (dict): Dicionário com informações do município
        var_types (list): Lista de tipos de variáveis a analisar. Se None, processa todas as variáveis.
        max_distance_km (float): Distância máxima em km do centro do município para considerar um ponto válido
    """
    try:
        # Abrir o dataset uma única vez
        ds = xr.open_dataset(nc_file)
        
        # Se var_types não for especificado, usar todas as variáveis disponíveis
        if var_types is None:
            var_types = list(VARIABLES.keys())
            
        # Verificar se todas as variáveis existem no arquivo
        var_names = [VARIABLES[var_type]['brams_name'] for var_type in var_types]
        missing_vars = [var for var in var_names if var not in ds.data_vars]
        if missing_vars:
            print(f"Erro: Variáveis não encontradas no arquivo NetCDF: {missing_vars}")
            print(f"Variáveis disponíveis: {list(ds.data_vars.keys())}")
            return None
            
        # Criar máscara do município uma única vez
        first_var = ds[var_names[0]].isel(time=0)
        lons, lats = np.meshgrid(first_var.lon.values, first_var.lat.values)
        points = np.column_stack((lons.flatten(), lats.flatten()))
        
        # Criar máscara vetorizada para pontos dentro do polígono
        mask = np.array([municipio_info['poligono'].contains(Point(lon, lat)) 
                        for lon, lat in points]).reshape(lons.shape)
        
        # Processar todas as variáveis
        resultados = {}
        for var_type in var_types:
            var_info = VARIABLES[var_type]
            var_name = var_info['brams_name']
            var_unit = var_info['unit']
            
            # Obter dados e aplicar máscara
            data = ds[var_name].isel(time=0)
            masked_data = np.where(mask, data.values, np.nan)
            
            # Criar array de distâncias do centro
            lons, lats = np.meshgrid(data.lon.values, data.lat.values)
            distances = np.array([
                Point(lon, lat).distance(municipio_info['centro']) * 111  # Converter para km
                for lon, lat in zip(lons.flatten(), lats.flatten())
            ]).reshape(lons.shape)
            
            # Aplicar máscara de distância
            distance_mask = distances <= max_distance_km
            masked_data = np.where(distance_mask, masked_data, np.nan)
            
            # Verificar se há dados válidos após a filtragem
            if np.all(np.isnan(masked_data)):
                print(f"AVISO: Nenhum dado válido encontrado para {var_type} dentro do raio de {max_distance_km}km")
                continue
            
            # Encontrar valores extremos
            max_value = float(np.nanmax(masked_data))
            min_value = float(np.nanmin(masked_data))
            
            # Verificar valores fisicamente possíveis
            if var_type == 'umidade':
                if min_value < 10 or max_value > 100:  # Umidade relativa deve estar entre 0-100%
                    print(f"AVISO: Valores de umidade fora do intervalo fisicamente possível: min={min_value}%, max={max_value}%")
                    # Ajustar para limites físicos
                    min_value = max(min_value, 0)
                    max_value = min(max_value, 100)
            
            # Encontrar índices dos valores extremos
            max_indices = np.unravel_index(np.nanargmax(masked_data), masked_data.shape)
            min_indices = np.unravel_index(np.nanargmin(masked_data), masked_data.shape)
            
            # Obter coordenadas dos pontos extremos
            max_lat = float(data.lat.values[max_indices[0]])
            max_lon = float(data.lon.values[max_indices[1]])
            min_lat = float(data.lat.values[min_indices[0]])
            min_lon = float(data.lon.values[min_indices[1]])
            
            # Calcular distâncias do centro
            max_point = Point(max_lon, max_lat)
            min_point = Point(min_lon, min_lat)
            max_distancia_centro = max_point.distance(municipio_info['centro']) * 111
            min_distancia_centro = min_point.distance(municipio_info['centro']) * 111
            
            # Formatar resultados
            resultados[var_type] = {
                "tipo_variavel": var_type,
                "nome_variavel": var_name,
                "maximo": {
                    "valor": max_value,
        "latitude": max_lat,
        "longitude": max_lon,
                    "localizacao": f"Lat: {max_lat:.2f}°, Lon: {max_lon:.2f}°",
                    "valor_formatado": f"{max_value:.1f}{var_unit}",
                    "distancia_centro_km": max_distancia_centro
                },
                "minimo": {
                    "valor": min_value,
                    "latitude": min_lat,
                    "longitude": min_lon,
                    "localizacao": f"Lat: {min_lat:.2f}°, Lon: {min_lon:.2f}°",
                    "valor_formatado": f"{min_value:.1f}{var_unit}",
                    "distancia_centro_km": min_distancia_centro
                },
                "municipio": municipio_info['nome'],
                "unidade": var_unit
            }
            
            # Verificar alertas
            if var_type in municipio_info.get('alerts', {}):
                alert_thresholds = municipio_info['alerts'][var_type]
                if max_value > alert_thresholds.get('max', float('inf')):
                    print(f"ALERTA: {var_type} acima do limite máximo ({alert_thresholds['max']}{var_unit})")
                if min_value < alert_thresholds.get('min', float('-inf')):
                    print(f"ALERTA: {var_type} abaixo do limite mínimo ({alert_thresholds['min']}{var_unit})")
            
            # Imprimir resultados
            print(f"\nValores extremos de {var_type} em {municipio_info['nome']}:")
            print(f"Máximo: {resultados[var_type]['maximo']['valor_formatado']}")
            print(f"Localização do máximo: {resultados[var_type]['maximo']['localizacao']}")
            print(f"Distância do centro (máximo): {max_distancia_centro:.1f} km")
            print(f"Mínimo: {resultados[var_type]['minimo']['valor_formatado']}")
            print(f"Localização do mínimo: {resultados[var_type]['minimo']['localizacao']}")
            print(f"Distância do centro (mínimo): {min_distancia_centro:.1f} km")
        
        return resultados
        
    except Exception as e:
        print(f"Erro ao calcular valores extremos: {e}")
        import traceback
        print("Rastreamento completo do erro:")
        print(traceback.format_exc())
        return None

def find_extreme_humidity(nc_file, municipio_info, max_distance_km=50):
    """
    Encontra os valores máximos e mínimos de umidade relativa dentro dos limites do município.
    """
    try:
        ds = xr.open_dataset(nc_file)
        data = ds['rh'].isel(time=0)
        
        # Selecionar a camada correta (mesmo que no plot)
        if len(data.dims) > 2:
            data = data.isel(lev_2=0)
        
        # Criar máscara do município
        lons, lats = np.meshgrid(data.lon.values, data.lat.values)
        points = np.column_stack((lons.flatten(), lats.flatten()))
        mask = np.array([municipio_info['poligono'].contains(Point(lon, lat)) 
                        for lon, lat in points]).reshape(lons.shape)
        
        # Aplicar máscara aos dados
        masked_data = np.where(mask, data.values, np.nan)
        
        # Criar array de distâncias do centro
        distances = np.array([
            Point(lon, lat).distance(municipio_info['centro']) * 111
            for lon, lat in zip(lons.flatten(), lats.flatten())
        ]).reshape(lons.shape)
        
        # Aplicar máscara de distância
        distance_mask = distances <= max_distance_km
        masked_data = np.where(distance_mask, masked_data, np.nan)
        
        # Encontrar valores extremos
        max_value = float(np.nanmax(masked_data))
        min_value = float(np.nanmin(masked_data))

        # Encontrar índices dos valores extremos
        max_indices = np.unravel_index(np.nanargmax(masked_data), masked_data.shape)
        min_indices = np.unravel_index(np.nanargmin(masked_data), masked_data.shape)
        
        # Obter coordenadas
        max_lat = float(data.lat.values[max_indices[0]])
        max_lon = float(data.lon.values[max_indices[1]])
        min_lat = float(data.lat.values[min_indices[0]])
        min_lon = float(data.lon.values[min_indices[1]])
        
        # Calcular distâncias
        max_point = Point(max_lon, max_lat)
        min_point = Point(min_lon, min_lat)
        max_distancia_centro = max_point.distance(municipio_info['centro']) * 111
        min_distancia_centro = min_point.distance(municipio_info['centro']) * 111
        
        resultado = {
            "tipo_variavel": "umidade",
            "nome_variavel": "rh",
            "maximo": {
                "valor": max_value,
                "latitude": max_lat,
                "longitude": max_lon,
                "localizacao": f"Lat: {max_lat:.2f}°, Lon: {max_lon:.2f}°",
                "valor_formatado": f"{max_value:.1f}%",
                "distancia_centro_km": max_distancia_centro
            },
            "minimo": {
                "valor": min_value,
                "latitude": min_lat,
                "longitude": min_lon,
                "localizacao": f"Lat: {min_lat:.2f}°, Lon: {min_lon:.2f}°",
                "valor_formatado": f"{min_value:.1f}%",
                "distancia_centro_km": min_distancia_centro
            },
            "municipio": municipio_info['nome'],
            "unidade": "%"
        }
        
        # Verificar alertas
        if "umidade" in municipio_info.get('alerts', {}):
            alert_thresholds = municipio_info['alerts']['umidade']
            if max_value > alert_thresholds.get('max', float('inf')):
                print(f"ALERTA: Umidade acima do limite máximo ({alert_thresholds['max']}%)")
            if min_value < alert_thresholds.get('min', float('-inf')):
                print(f"ALERTA: Umidade abaixo do limite mínimo ({alert_thresholds['min']}%)")
        
        return resultado
        
    except Exception as e:
        print(f"Erro ao calcular valores extremos de umidade: {e}")
        return None

def find_extreme_temperature(nc_file, municipio_info, max_distance_km=50):
    """
    Encontra os valores máximos e mínimos de temperatura dentro dos limites do município.
    
    Args:
        nc_file (str): Caminho do arquivo NetCDF
        municipio_info (dict): Dicionário com informações do município
        max_distance_km (float): Distância máxima em km do centro do município para considerar um ponto válido
    """
    try:
        # Abrir o dataset uma única vez
        ds = xr.open_dataset(nc_file)
        
        # Verificar se a variável existe no arquivo
        var_name = VARIABLES['temperature']['brams_name']
        if var_name not in ds.data_vars:
            print(f"Erro: Variável '{var_name}' não encontrada no arquivo NetCDF")
            print(f"Variáveis disponíveis: {list(ds.data_vars.keys())}")
            return None
            
        # Criar máscara do município uma única vez
        data = ds[var_name].isel(time=0)
        lons, lats = np.meshgrid(data.lon.values, data.lat.values)
        points = np.column_stack((lons.flatten(), lats.flatten()))
        
        # Criar máscara vetorizada para pontos dentro do polígono
        mask = np.array([municipio_info['poligono'].contains(Point(lon, lat)) 
                        for lon, lat in points]).reshape(lons.shape)
        
        # Obter dados e aplicar máscara
        masked_data = np.where(mask, data.values, np.nan)
        
        # Criar array de distâncias do centro
        lons, lats = np.meshgrid(data.lon.values, data.lat.values)
        distances = np.array([
            Point(lon, lat).distance(municipio_info['centro']) * 111  # Converter para km
            for lon, lat in zip(lons.flatten(), lats.flatten())
        ]).reshape(lons.shape)
        
        # Aplicar máscara de distância
        distance_mask = distances <= max_distance_km
        masked_data = np.where(distance_mask, masked_data, np.nan)
        
        # Verificar se há dados válidos após a filtragem
        if np.all(np.isnan(masked_data)):
            print(f"AVISO: Nenhum dado válido encontrado para temperatura dentro do raio de {max_distance_km}km")
            return None
        
        # Encontrar valores extremos
        max_value = float(np.nanmax(masked_data))
        min_value = float(np.nanmin(masked_data))
        
        # Encontrar índices dos valores extremos
        max_indices = np.unravel_index(np.nanargmax(masked_data), masked_data.shape)
        min_indices = np.unravel_index(np.nanargmin(masked_data), masked_data.shape)
        
        # Obter coordenadas dos pontos extremos
        max_lat = float(data.lat.values[max_indices[0]])
        max_lon = float(data.lon.values[max_indices[1]])
        min_lat = float(data.lat.values[min_indices[0]])
        min_lon = float(data.lon.values[min_indices[1]])
        
        # Calcular distâncias do centro
        max_point = Point(max_lon, max_lat)
        min_point = Point(min_lon, min_lat)
        max_distancia_centro = max_point.distance(municipio_info['centro']) * 111
        min_distancia_centro = min_point.distance(municipio_info['centro']) * 111
        
        # Formatar resultados
        resultado = {
            "tipo_variavel": "temperature",
            "nome_variavel": var_name,
            "maximo": {
                "valor": max_value,
                "latitude": max_lat,
                "longitude": max_lon,
                "localizacao": f"Lat: {max_lat:.2f}°, Lon: {max_lon:.2f}°",
                "valor_formatado": f"{max_value:.1f}°C",
                "distancia_centro_km": max_distancia_centro
            },
            "minimo": {
                "valor": min_value,
                "latitude": min_lat,
                "longitude": min_lon,
                "localizacao": f"Lat: {min_lat:.2f}°, Lon: {min_lon:.2f}°",
                "valor_formatado": f"{min_value:.1f}°C",
                "distancia_centro_km": min_distancia_centro
            },
            "municipio": municipio_info['nome'],
            "unidade": "°C"
        }
        
        # Verificar alertas
        if "temperature" in municipio_info.get('alerts', {}):
            alert_thresholds = municipio_info['alerts']['temperature']
            if max_value > alert_thresholds.get('max', float('inf')):
                print(f"ALERTA: Temperatura acima do limite máximo ({alert_thresholds['max']}°C)")
            if min_value < alert_thresholds.get('min', float('-inf')):
                print(f"ALERTA: Temperatura abaixo do limite mínimo ({alert_thresholds['min']}°C)")
        
        # Imprimir resultados
        print(f"\nValores extremos de temperatura em {municipio_info['nome']}:")
        print(f"Máximo: {resultado['maximo']['valor_formatado']}")
        print(f"Localização do máximo: {resultado['maximo']['localizacao']}")
        print(f"Distância do centro (máximo): {max_distancia_centro:.1f} km")
        print(f"Mínimo: {resultado['minimo']['valor_formatado']}")
        print(f"Localização do mínimo: {resultado['minimo']['localizacao']}")
        print(f"Distância do centro (mínimo): {min_distancia_centro:.1f} km")
        
        return resultado
        
    except Exception as e:
        print(f"Erro ao calcular valores extremos de temperatura: {e}")
        import traceback
        print("Rastreamento completo do erro:")
        print(traceback.format_exc())
        return None

def read_municipios_shapefile():
    """Lê o shapefile dos municípios de Goiás."""
    # Obter caminho absoluto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    shapefile_path = os.path.join(current_dir, "..", "files", "GO_Municipios_2024", "GO_Municipios_2024.shp")
    
    try:
        # Imprimir o caminho absoluto para depuração
        print(f"Tentando ler o shapefile de: {shapefile_path}")
        
        # Verificar se o arquivo existe
        if not os.path.exists(shapefile_path):
            print(f"Shapefile não encontrado em: {shapefile_path}")
            return None
            
        # Ler o shapefile
        gdf = gpd.read_file(shapefile_path)
        print(f"Shapefile carregado com sucesso: {len(gdf)} municípios encontrados")
        return gdf
    except Exception as e:
        print(f"Erro ao ler o shapefile: {e}")
        # Imprimir informações detalhadas do erro
        import traceback
        print("Rastreamento completo do erro:")
        print(traceback.format_exc())
        return None

def find_municipio_by_code(municipios_gdf, codigo_ibge):
    try:
        # Criar um dicionário de cache para códigos IBGE se ainda não existir
        if not hasattr(find_municipio_by_code, 'cache'):
            find_municipio_by_code.cache = {}
            # Pré-processar todos os códigos IBGE uma única vez
            find_municipio_by_code.cache = {
                str(row['CD_MUN']): {
                    'codigo_ibge': row['CD_MUN'],
                    'nome': row['NM_MUN'],
                    'poligono': row.geometry,
                    'centro': row.geometry.centroid,

                    'dados': row.to_dict()
                }
                for _, row in municipios_gdf.iterrows()
            }
        
        # Buscar no cache
        codigo_str = str(codigo_ibge)
        if codigo_str in find_municipio_by_code.cache:
            return find_municipio_by_code.cache[codigo_str]
        
        print(f"\nMunicípio com código {codigo_ibge} não encontrado")
        return None
        
    except Exception as e:
        print(f"Erro ao buscar município: {e}")
        return None

def update_cities_polygons(municipios_gdf):
    try:
        # Limpar o cache anterior se existir
        if hasattr(find_municipio_by_code, 'cache'):
            del find_municipio_by_code.cache
        
        # Processar todas as cidades de uma vez
        resultados = {}
        for city_name, city_info in CITIES.items():
            print(f"\nBuscando polígono para {city_name}...")
            municipio_info = find_municipio_by_code(municipios_gdf, city_info['ibge_code'])
            resultados[city_name] = municipio_info
        
        # Atualizar CITIES em um único loop
        for city_name, municipio_info in resultados.items():
            if municipio_info:
                CITIES[city_name].update({
                    'polygon': municipio_info['poligono'],
                    'centro': municipio_info['centro'],

                })
                print(f"Polígono dos limites encontrados para {city_name}")

                print(f"Centro: Lat {municipio_info['centro'].y:.4f}°, Lon {municipio_info['centro'].x:.4f}°")
            else:
                print(f"ERRO: Não foi possível encontrar o polígono para {city_name}")
        
        return True
        
    except Exception as e:
        print(f"Erro ao atualizar polígonos das cidades: {e}")
        return False

if __name__ == "__main__":
    try:
        # Usar a data específica
        date = "20250518"  # Data fixa para o exemplo
        print(f"Usando data: {date[:4]}-{date[4:6]}-{date[6:8]}")
        
        # Baixar todos os arquivos do dia
        downloaded_files = download_cempa_files(date)
        
        if not downloaded_files:
            print("Nenhum arquivo foi baixado. Encerrando execução.")
            exit(1)

        # Ler shapefile dos municípios
        municipios = read_municipios_shapefile()

        if municipios is not None:
            # Atualizar polígonos de todas as cidades
            if update_cities_polygons(municipios):
                print("\nPolígonos dos limites atualizados com sucesso para todas as cidades!")
                
                # Usar os dados das cidades
                for city_name, city_info in CITIES.items():
                    if city_info['polygon'] is not None:
                        print(f"\nDados disponíveis para {city_name}:")
                        print(f"Código IBGE: {city_info['ibge_code']}")
                        print(f"Centro: Lat {city_info['centro'].y:.4f}°, Lon {city_info['centro'].x:.4f}°")

        # Processar cada par de arquivos (CTL e GRA)
        for ctl_path, gra_path in downloaded_files:
            # Extrair a hora do nome do arquivo
            hour = ctl_path.split('-')[-2][:2]  # Pega os dois primeiros dígitos da hora
            print(f"\nProcessando arquivos da hora {hour}:00...")
            
            # Converter para NetCDF
            output_nc = f"./files/saida_{hour}.nc"
            if convert_to_netcdf(ctl_path, output_nc):
                # Gerar plot de umidade relativa
                output_plot = f"./files/humidity_plot_{date}_{hour}.png"
                print(f"\nGerando plot de umidade relativa para {hour}:00...")
                plot_humidity(output_nc, f"{date}{hour}00", output_plot)
                
                # Processar todas as cidades para este horário
                for city_name, city_info in CITIES.items():
                    if city_info['polygon'] is not None:
                        print(f"\nAnalisando {city_name} para {hour}:00...")

                        # Analisar temperatura
                        temperature_result = find_extreme_temperature(output_nc, {
                            'nome': city_name,
                            'poligono': city_info['polygon'],
                            'centro': city_info['centro'],
                            'alerts': city_info.get('alerts', {})
                        }, 100)

                        # Analisar umidade
                        umid_result = find_extreme_humidity(output_nc, {
                            'nome': city_name,
                            'poligono': city_info['polygon'],
                            'centro': city_info['centro'],
                            'alerts': city_info.get('alerts', {})
                        }, 100)

                        # Imprimir resultados da umidade (a temperatura já imprime seus resultados)
                        if umid_result:
                            print(f"\nValores extremos de umidade em {city_name} para {hour}:00:")
                            print(f"Máximo: {umid_result['maximo']['valor_formatado']}")
                            print(f"Localização do máximo: {umid_result['maximo']['localizacao']}")
                            print(f"Distância do centro (máximo): {umid_result['maximo']['distancia_centro_km']:.1f} km")
                            print(f"Mínimo: {umid_result['minimo']['valor_formatado']}")
                            print(f"Localização do mínimo: {umid_result['minimo']['localizacao']}")
                            print(f"Distância do centro (mínimo): {umid_result['minimo']['distancia_centro_km']:.1f} km")

    finally:
        # Limpar o cache ao finalizar
        if hasattr(find_municipio_by_code, 'cache'):
            del find_municipio_by_code.cache