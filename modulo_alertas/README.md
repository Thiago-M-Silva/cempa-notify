# CEMPA-Notify: Sistema de Alertas Meteorológicos

Sistema automatizado para processamento de dados meteorológicos, detecção de condições extremas e geração de alertas para municípios específicos.

## Visão Geral

Este módulo faz parte do sistema CEMPA-Notify, responsável por analisar dados meteorológicos do CEMPA (Centro de Excelência em Meteorologia e Previsão do Ambiente - UFG), identificar condições meteorológicas extremas (temperatura, umidade, etc.) e gerar alertas quando essas condições ultrapassam limites pré-configurados.

## Pré-requisitos

O sistema requer as seguintes ferramentas:

1. **CDO (Climate Data Operators)**: Ferramenta para manipulação e análise de dados climáticos
   - Instalação: `brew install cdo` (macOS) ou `apt-get install cdo` (Ubuntu/Debian)
   - [Documentação CDO](https://code.mpimet.mpg.de/projects/cdo)

2. **pipx**: Gerenciador de instalação de aplicações Python
   - [Guia de instalação](https://pipx.pypa.io/stable/installation/)

3. **Poetry**: Gerenciador de dependências e pacotes para Python
   - Instalação via pipx: `pipx install poetry`
   - [Documentação Poetry](https://python-poetry.org/docs/)

4. **Shapefiles do IBGE**: Arquivos com limites geográficos dos municípios
   - Download: [Malhas territoriais do IBGE](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html?=&t=downloads)
   - Necessário para delimitar a área dos municípios analisados

## Estrutura do Projeto

```
modulo_alertas/
├── src/                      # Código-fonte principal
│   ├── main.py               # Script principal com lógica de processamento
│   ├── file_utils.py         # Utilitários para download e manipulação de arquivos
│   └── __init__.py
├── files/                    # Diretório para armazenar arquivos baixados e processados
├── pyproject.toml            # Configuração do Poetry e dependências
├── poetry.lock               # Versões fixas das dependências
└── README.md                 # Esta documentação
```

## Instalação

1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd cempa-notify/modulo_alertas
   ```

2. Instale as dependências usando Poetry:
   ```bash
   poetry install
   ```

## Uso

Execute o script principal usando Poetry:

```bash
poetry run python src/main.py
```

## Funcionamento Detalhado

O sistema opera em quatro etapas principais:

### 1. Download de Dados Meteorológicos

- Conecta-se ao servidor do CEMPA (https://tatu.cempa.ufg.br/) e baixa os arquivos de previsão meteorológica no formato CTL/GRA
- Os arquivos são baixados para a pasta `files/` e organizados por data
- São obtidos dados para múltiplos horários do dia atual para análise temporal

### 2. Carregamento de Informações Geográficas

- Carrega shapefiles do IBGE contendo os limites territoriais dos municípios de Goiás
- Extrai os polígonos correspondentes aos municípios configurados no sistema (atualmente Goiânia e Rio Verde)
- Calcula os centros geométricos dos municípios para uso na análise espacial

### 3. Conversão e Processamento de Dados

- Converte os arquivos CTL/GRA para formato NetCDF usando a ferramenta CDO
- O formato NetCDF facilita o processamento científico dos dados com a biblioteca xarray
- Os dados são carregados e filtrados espacialmente para cada município de interesse

### 4. Análise e Geração de Alertas

- Para cada município configurado, analisa variáveis meteorológicas (temperatura, umidade)
- Identifica valores máximos e mínimos dentro do limite territorial ou raio de distância do centro
- Compara os valores encontrados com limiares configurados (ex: temperatura > 35°C ou umidade < 20%)
- Gera alertas quando condições extremas são detectadas

## Configuração

O sistema é configurado através do dicionário `VARIABLES` no arquivo `main.py`:

```python
VARIABLES = {
    "temperature": {
        "name": "Temperatura",
        "unit": "°C",
        "brams_name": "t2mj",
    },
    "umidade": {
        "name": "Umidade",
        "unit": "%",
        "brams_name": "rh",
        "dimension": "lev_2",
    }
}
```

Os municípios e limiares de alerta são configurados no dicionário `CITIES`:

```python
CITIES = {
    "Goiânia": {
        "ibge_code": 5208707,
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
    },
}
```

## Extensão

Para adicionar novas variáveis meteorológicas:
1. Adicione a configuração no dicionário `VARIABLES`
2. Defina nome, unidade e nome da variável nos arquivos BRAMS
3. Se a variável tiver dimensões extras, defina a propriedade `dimension`

Para adicionar novos municípios:
1. Adicione a configuração no dicionário `CITIES`
2. Inclua o código IBGE do município e os limiares de alerta desejados
