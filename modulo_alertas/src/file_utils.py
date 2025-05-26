import os
import requests
from urllib.parse import urljoin
import datetime

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
    files_dir = "./tmp_files"
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
            print(f"\nArquivos para hora {hour_str}:00 já existem, pulando download...")
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
            # Remove arquivos parciais em caso de erro
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
