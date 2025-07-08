# CEMPA-Notify: Sistema de Alertas Meteorológicos

Sistema automatizado para processamento de dados meteorológicos, detecção de condições extremas e geração de alertas para municípios específicos.

## Visão Geral

Este módulo faz parte do sistema CEMPA-Notify, responsável por analisar dados meteorológicos do CEMPA (Centro de Excelência em Meteorologia e Previsão do Ambiente - UFG), identificar condições meteorológicas extremas (temperatura, umidade, etc.) e gerar alertas quando essas condições ultrapassam limites pré-configurados.

## Pré-requisitos

O sistema requer as seguintes ferramentas:

1. **Flask**: ferramenta que permite a criação de um servidor
2. **flask_sqlalchemy**: ferramenta para a comunicação do sistema com o banco de dados
3. **flask-cors**: ferramenta que complementa o servidor permitindo que receba requisições de diversas fontes

Todas as ferramentas acima podem ser instaladas com o comando: `pip install -r requirements.txt`

## Estrutura do Projeto

```
modulo_usuarios/
├── src/                      # Código-fonte principal
|   ├── static                # Imagens utilizadas na tela de cadastro
│   ├──  __init__.py          # Script principal com lógica de processamento
│   ├── form.py               # Arquivo que gera o formulário de cadastro
|   ├── models.py             # Modelos das tabelas a serem persistidas no banco de dados
|   ├── routes.py             # API para receber os dados dos usuários cadastrados
│   └── services.py           # Lógica para armazenamento de dados
├── requirements.txt          # Lista das ferramentas utilizadas neste módulo
├── run.py                    # Arquivo que inicia a execução do projeto
└── README.md                 # Esta documentação
```

## Instalação

1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd cempa-notify/modulo_usuarios
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Execute o arquivo principal:

```bash
python run.py
```
O módulo de usuarios estará disponível em http://localhost:8081 onde será visível a tela de cadastro