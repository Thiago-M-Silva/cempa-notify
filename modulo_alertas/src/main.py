import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
import numpy as np
import subprocess
import os
from urllib.parse import urljoin
import datetime
import geopandas as gpd
from shapely.geometry import Point
from functools import lru_cache
import hashlib
import time
from file_utils import download_cempa_files, clean_old_files
from datetime import datetime 
import sys

pathFiles = "/tmp/cempa"

# Adicionar o diretório raiz ao path para permitir importações absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared_config.cempa_config import VALID_CITIES, VALID_ALERT_TYPES, CITY_NAMES

# Construir o dicionário CITIES a partir das configurações compartilhadas
CITIES = {}
for city_name, city_data in VALID_CITIES.items():
    CITIES[city_name] = {
        "ibge_code": city_data["ibge_code"],
        "polygon": None,  # Será preenchido durante a execução
        "centro": None,   # Será preenchido durante a execução
        "alerts": city_data["alerts"]  # Usa os thresholds diretamente da configuração
    }

@lru_cache(maxsize=32)  # Cache para os últimos 32 arquivos processados
def get_cached_variable(nc_file, var_name, time_idx=0):
    """
    Obtém uma variável do arquivo NetCDF com cache.
    O cache é baseado no nome do arquivo, variável e índice de tempo.
    """
    # Gera uma chave única para o cache baseada no arquivo e variável
    file_hash = hashlib.md5(f"{nc_file}_{var_name}_{time_idx}".encode()).hexdigest()
    
    try:
        with xr.open_dataset(nc_file, 
                           variables=[var_name],  # Carrega apenas a variável necessária
                           chunks={'time': 1}) as ds:
            return ds[var_name].isel(time=time_idx).values
    except Exception as e:
        print(f"Erro ao processar variável {var_name} do arquivo {nc_file}: {e}")
        return None

def clear_cache():
    """Limpa o cache quando necessário"""
    get_cached_variable.cache_clear()

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
    ds = xr.open_dataset(nc_file, 
                        chunks={'time': 1},  # Carrega apenas um timestep por vez
                        cache=False,         # Evita cache desnecessário
                        decode_times=False)  # Desativa decodificação de tempos se não necessário
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
    ds = xr.open_dataset(nc_file, 
                        chunks={'time': 1},  # Carrega apenas um timestep por vez
                        cache=False,         # Evita cache desnecessário
                        decode_times=False)  # Desativa decodificação de tempos se não necessário
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

# Dicionário que define as propriedades de cada variável meteorológica processada pelo sistema
# Cada entrada contém configurações específicas para uma variável meteorológica
VARIABLES = {
    # Configuração para variável de temperatura
    "temperature": {
        "name": "Temperatura",      # Nome de exibição da variável
        "unit": "°C",               # Unidade de medida (para formatação de valores)
        "brams_name": "t2mj",       # Nome da variável nos arquivos BRAMS NetCDF
        # Não possui 'dimension' pois não requer tratamento especial de dimensões
    },
    # Configuração para variável de umidade
    "humidity": {
        "name": "Umidade",          # Nome de exibição da variável
        "unit": "%",                # Unidade de medida (para formatação de valores)
        "brams_name": "rh",         # Nome da variável nos arquivos BRAMS NetCDF
        "dimension": "lev_2",       # Indica que esta variável possui uma dimensão extra (lev_2)
                                    # que deve ser tratada especialmente na função find_extreme
    }
    # Para adicionar novas variáveis meteorológicas:
    # 1. Crie uma nova entrada com chave única
    # 2. Defina pelo menos name, unit e brams_name
    # 3. Adicione dimension: "lev_2" se a variável requer seleção de nível
}

def find_extreme(nc_file, municipio_info, variable, max_distance_km=50):
    """
    Função genérica para encontrar valores extremos de uma variável meteorológica.
    
    Args:
        nc_file (str): Caminho do arquivo NetCDF
        municipio_info (dict): Dicionário com informações do município
        variable (dict): Objeto de variável (item do dicionário VARIABLES)
        max_distance_km (float): Distância máxima em km do centro do município
        
    Returns:
        dict: Dicionário com os valores extremos encontrados
    """
    try:
        # Extrair informações importantes da variável
        var_name = variable['brams_name']
        unit = variable['unit']
        var_type = next((k for k, v in VARIABLES.items() if v['brams_name'] == var_name), None)
        var_display_name = variable.get('name', var_name)
        
        if not var_type:
            print(f"Erro: Variável com brams_name '{var_name}' não encontrada em VARIABLES")
            return None
            
        # Abrir o dataset
        ds = xr.open_dataset(nc_file)
        
        # Verificar se a variável existe no arquivo
        if var_name not in ds.data_vars:
            print(f"Erro: Variável '{var_name}' não encontrada no arquivo NetCDF")
            print(f"Variáveis disponíveis: {list(ds.data_vars.keys())}")
            return None
            
        # Obter dados
        data = ds[var_name].isel(time=0)
        
        # Verificar dimensões e aplicar isel se necessário
        if 'dimension' in variable and variable['dimension'] == 'lev_2' and 'lev_2' in data.dims:
            data = data.isel(lev_2=0)
        
        # Criar máscara do município
        lons, lats = np.meshgrid(data.lon.values, data.lat.values)
        points = np.column_stack((lons.flatten(), lats.flatten()))
        
        # Criar máscara vetorizada para pontos dentro do polígono
        mask = np.array([municipio_info['poligono'].contains(Point(lon, lat)) 
                        for lon, lat in points]).reshape(lons.shape)
        
        # Aplicar máscara aos dados
        masked_data = np.where(mask, data.values, np.nan)
        
        # Criar array de distâncias do centro
        distances = np.array([
            Point(lon, lat).distance(municipio_info['centro']) * 111  # Converter para km
            for lon, lat in zip(lons.flatten(), lats.flatten())
        ]).reshape(lons.shape)
        
        # Aplicar máscara de distância
        distance_mask = distances <= max_distance_km
        masked_data = np.where(distance_mask, masked_data, np.nan)
        
        # Verificar se há dados válidos após a filtragem
        if np.all(np.isnan(masked_data)):
            print(f"AVISO: Nenhum dado válido encontrado para {var_display_name} dentro do raio de {max_distance_km}km")
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
            "tipo_variavel": var_type,
            "nome_variavel": var_name,
            "maximo": {
                "valor": max_value,
                "latitude": max_lat,
                "longitude": max_lon,
                "localizacao": f"Lat: {max_lat:.2f}°, Lon: {max_lon:.2f}°",
                "valor_formatado": f"{max_value:.1f}{unit}",
                "distancia_centro_km": max_distancia_centro
            },
            "minimo": {
                "valor": min_value,
                "latitude": min_lat,
                "longitude": min_lon,
                "localizacao": f"Lat: {min_lat:.2f}°, Lon: {min_lon:.2f}°",
                "valor_formatado": f"{min_value:.1f}{unit}",
                "distancia_centro_km": min_distancia_centro
            },
            "municipio": municipio_info['nome'],
            "unidade": unit
        }
        
        # Verificar alertas usando os thresholds específicos da cidade
        if var_type in municipio_info.get('alerts', {}) and 'nome' in municipio_info:
            # Obter os thresholds específicos para esta cidade
            cidade_nome = municipio_info['nome']
            
            # Verificar se temos thresholds específicos para esta cidade e variável
            if cidade_nome in CITIES and var_type in CITIES[cidade_nome]['alerts']:
                alert_thresholds = CITIES[cidade_nome]['alerts'][var_type]
                
                # Verificar máximo
                if max_value > alert_thresholds.get('max', float('inf')):
                    print(f"ALERTA: {var_display_name} acima do limite máximo em {cidade_nome} ({alert_thresholds['max']}{unit})")
                
                # Verificar mínimo
                if min_value < alert_thresholds.get('min', float('-inf')):
                    print(f"ALERTA: {var_display_name} abaixo do limite mínimo em {cidade_nome} ({alert_thresholds['min']}{unit})")
        
        # Imprimir resultados
        print(f"\nValores extremos de {var_display_name} em {municipio_info['nome']}:")
        print(f"Máximo: {resultado['maximo']['valor_formatado']}")
        print(f"Localização do máximo: {resultado['maximo']['localizacao']}")
        print(f"Distância do centro (máximo): {max_distancia_centro:.1f} km")
        print(f"Mínimo: {resultado['minimo']['valor_formatado']}")
        print(f"Localização do mínimo: {resultado['minimo']['localizacao']}")
        print(f"Distância do centro (mínimo): {min_distancia_centro:.1f} km")
        
        return resultado
        
    except Exception as e:
        print(f"Erro ao calcular valores extremos de {var_display_name if 'var_display_name' in locals() else 'variável'}: {e}")
        import traceback
        print("Rastreamento completo do erro:")
        print(traceback.format_exc())
        return None

# Compatibilidade com funções existentes
def find_extreme_temperature(nc_file, municipio_info, max_distance_km=50):
    return find_extreme(nc_file, municipio_info, VARIABLES['temperature'], max_distance_km)

def find_extreme_humidity(nc_file, municipio_info, max_distance_km=50):
    return find_extreme(nc_file, municipio_info, VARIABLES['umidade'], max_distance_km)

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
    start_time = time.time()
    
    try:
        # Usar a data atual
        date = datetime.now().strftime("%Y%m%d")  # Formato: YYYYMMDD
        print(f"Usando data: {date[:4]}-{date[4:6]}-{date[6:8]}")

        clean_old_files()
        
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
                        print(f"Alertas configurados:")
                        for alert_type, thresholds in city_info['alerts'].items():
                            print(f"  - {alert_type}: min={thresholds['min']}, max={thresholds['max']}")

        # Processar cada par de arquivos (CTL e GRA)
        for ctl_path, gra_path in downloaded_files:
            # Extrair a hora do nome do arquivo
            hour = ctl_path.split('-')[-2][:2]  # Pega os dois primeiros dígitos da hora
            print(f"\nProcessando arquivos da hora {hour}:00...")
            
            # Converter para NetCDF
            # Extrair o nome base do arquivo original para usar no output
            base_filename = os.path.basename(ctl_path).replace('.ctl', '')
            output_nc = f"{pathFiles}/{base_filename}.nc"
            if convert_to_netcdf(ctl_path, output_nc):
                # Processar todas as cidades para este horário
                for city_name, city_info in CITIES.items():
                    if city_info['polygon'] is not None:
                        print(f"\nAnalisando {city_name} para {hour}:00...")
                        
                        # Criar um dicionário de informações para a cidade atual
                        city_data = {
                            'nome': city_name,
                            'poligono': city_info['polygon'],
                            'centro': city_info['centro'],
                            'alerts': city_info['alerts']
                        }
                        
                        # Analisar cada tipo de alerta configurado para a cidade
                        for alert_type in VALID_ALERT_TYPES:                                
                            if alert_type in VARIABLES:
                                print(f"\nVerificando {alert_type} para {city_name}...")
                                result = find_extreme(output_nc, city_data, VARIABLES[alert_type], 100)
                                
                                if result:
                                    print(f"Análise de {alert_type} para {city_name} concluída com sucesso.")
                                else:
                                    print(f"Falha ao analisar {alert_type} para {city_name}.")

    finally:
        # Limpar o cache ao finalizar
        if hasattr(find_municipio_by_code, 'cache'):
            del find_municipio_by_code.cache
        
        # Calcular e mostrar o tempo total de execução
        execution_time = time.time() - start_time
        print(f"\n{'='*50}\nTempo total de execução:\n"
              f"{f'{int(execution_time//3600)}h {int((execution_time%3600)//60)}m {execution_time%60:.2f}s' if execution_time >= 3600 else f'{int(execution_time//60)}m {execution_time%60:.2f}s' if execution_time >= 60 else f'{execution_time:.2f}s'}\n{'='*50}")