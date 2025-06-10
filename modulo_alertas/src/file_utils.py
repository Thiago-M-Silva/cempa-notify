import os
import requests
from urllib.parse import urljoin
import datetime
import shutil
import glob

pathFiles = "/tmp/cempa"

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
    Verifica se os arquivos já existem antes de baixar.
    
    Args:
        date (str, optional): Data no formato YYYYMMDD. Se None, usa a data atual.
        hours (list, optional): Lista de horas para baixar (0-23). Se None, baixa todas as horas.
    """
    if date is None:
        date = datetime.datetime.now().strftime("%Y%m%d")
    
    if hours is None:
        hours = range(24)
    
    downloaded_files = []
    files_dir = pathFiles
    os.makedirs(files_dir, exist_ok=True)
    
    for hour in hours:
        hour_str = f"{hour:02d}"
        base_url = f"https://tatu.cempa.ufg.br/BRAMS-dataout/{date}00/"
        file_prefix = f"Go5km-A-{date[:4]}-{date[4:6]}-{date[6:8]}-{hour_str}0000-g1"
        
        ctl_url = urljoin(base_url, f"{file_prefix}.ctl")
        gra_url = urljoin(base_url, f"{file_prefix}.gra")
        
        ctl_path = os.path.join(files_dir, f"{file_prefix}.ctl")
        gra_path = os.path.join(files_dir, f"{file_prefix}.gra")
        
        if os.path.exists(ctl_path) and os.path.exists(gra_path):
            print(f"Arquivos para hora {hour_str}:00 já existem, pulando download...")
            downloaded_files.append((ctl_path, gra_path))
            continue
        
        try:
            print(f"\nBaixando arquivos para hora {hour_str}:00...")
            
            # Baixa apenas o arquivo que não existe
            if not os.path.exists(ctl_path):
                print(f"Baixando {ctl_url}...")
                download_file(ctl_url, ctl_path)
            else:
                print(f"Arquivo CTL já existe: {ctl_path}")
            
            if not os.path.exists(gra_path):
                print(f"Baixando {gra_url}...")
                download_file(gra_url, gra_path)
            else:
                print(f"Arquivo GRA já existe: {gra_path}")
            
            print(f"Downloads concluídos com sucesso para hora {hour_str}:00!")
            downloaded_files.append((ctl_path, gra_path))
            
        except requests.RequestException as e:
            print(f"Erro ao baixar arquivos para hora {hour_str}:00: {e}")
            if os.path.exists(ctl_path):
                os.remove(ctl_path)
            if os.path.exists(gra_path):
                os.remove(gra_path)
            continue
    
    if downloaded_files:
        print(f"\nTotal de arquivos disponíveis: {len(downloaded_files)}")
        return downloaded_files
    else:
        print("\nNenhum arquivo está disponível.")
        return None

def clean_old_files(directory=pathFiles, file_pattern="*.ctl,*.gra,HST*-MeteogramASC.out"):
    """
    Remove arquivos que não são do dia atual do diretório especificado.
    Deleta permanentemente os arquivos sem enviá-los para a lixeira.
    
    Args:
        directory (str): Diretório onde os arquivos estão armazenados
        file_pattern (str): Padrões de arquivos a serem verificados, separados por vírgula
    
    Returns:
        tuple: (quantidade de arquivos removidos, espaço liberado em bytes)
    """
    if not os.path.exists(directory):
        print(f"Diretório {directory} não existe.")
        return 0, 0
    
    remove_nc_files(directory)
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today_date = datetime.datetime.strptime(today, "%Y-%m-%d").date()
    
    patterns = file_pattern.split(',')
    all_files = []
    
    for pattern in patterns:
        pattern_path = os.path.join(directory, pattern.strip())
        all_files.extend(glob.glob(pattern_path))
    
    deleted_count = 0
    freed_space = 0
    
    for file_path in all_files:
        if not os.path.isfile(file_path):
            continue
        
        filename = os.path.basename(file_path)
        
        # Verificar se é um arquivo de meteograma (formato HST*-MeteogramASC.out)
        if filename.startswith("HST") and filename.endswith("-MeteogramASC.out"):
            try:
                # Extrair a data do nome do arquivo (formato: HST2025042900-MeteogramASC.out)
                # onde 2025 é o ano, 04 é o mês e 29 é o dia
                date_part = filename[3:11]  # Extrai "20250429"
                if len(date_part) >= 8:
                    year = int(date_part[0:4])
                    month = int(date_part[4:6])
                    day = int(date_part[6:8])
                    
                    file_date = datetime.datetime(year, month, day).date()
                    
                    if file_date < today_date:
                        file_size = os.path.getsize(file_path)
                        freed_space += file_size
                        
                        # Deletar o arquivo permanentemente
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            print(f"Removido arquivo de meteograma antigo: {filename}")
                        except Exception as e:
                            print(f"Erro ao remover arquivo {file_path}: {e}")
                            
            except Exception as e:
                print(f"Erro ao processar arquivo de meteograma {file_path}: {e}")
        else:
            # Extrair a data do nome do arquivo (assumindo formato Go5km-A-YYYY-MM-DD-...)
            try:
                parts = filename.split('-')
                if len(parts) >= 5:  # Formato esperado: Go5km-A-YYYY-MM-DD-...
                    file_date_str = f"{parts[2]}-{parts[3]}-{parts[4]}"
                    file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
                    
                    if file_date < today_date:
                        file_size = os.path.getsize(file_path)
                        freed_space += file_size
                        
                        # Deletar o arquivo permanentemente
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                        except Exception as e:
                            print(f"Erro ao remover arquivo {file_path}: {e}")
            except Exception as e:
                print(f"Erro ao processar arquivo {file_path}: {e}")
    
    freed_space_mb = freed_space / (1024 * 1024)
    print(f"\nLimpeza concluída. {deleted_count} arquivos removidos, liberando {freed_space_mb:.2f} MB de espaço.")
    
    return deleted_count, freed_space

def remove_nc_files(directory=pathFiles):
    """
    Remove todos os arquivos com extensão .nc do diretório especificado.
    Deleta permanentemente os arquivos sem enviá-los para a lixeira.
    
    Args:
        directory (str): Diretório onde os arquivos estão armazenados
    
    Returns:
        tuple: (quantidade de arquivos removidos, espaço liberado em bytes)
    """
    if not os.path.exists(directory):
        print(f"Diretório {directory} não existe.")
        return 0, 0
    
    # Encontrar todos os arquivos .nc
    nc_pattern = os.path.join(directory, "*.nc")
    nc_files = glob.glob(nc_pattern)
    
    print(f"Encontrados {len(nc_files)} arquivos .nc para remoção...")
    
    deleted_count = 0
    freed_space = 0
    
    for file_path in nc_files:
        if not os.path.isfile(file_path):
            continue
        
        try:
            file_size = os.path.getsize(file_path)
            os.remove(file_path)
            freed_space += file_size
            deleted_count += 1
        except Exception as e:
            print(f"Erro ao remover arquivo {file_path}: {e}")
    
    freed_space_mb = freed_space / (1024 * 1024)
    print(f"\nLimpeza concluída. {deleted_count} arquivos .nc removidos, liberando {freed_space_mb:.2f} MB de espaço.")
    
    return deleted_count, freed_space
