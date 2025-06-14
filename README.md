# CEMPA Notify - Sistema de Alertas Meteorológicos

Sistema de alertas meteorológicos que monitora condições de temperatura e umidade, enviando notificações por email para usuários cadastrados.

## Índice
- [CEMPA Notify - Sistema de Alertas Meteorológicos](#cempa-notify---sistema-de-alertas-meteorológicos)
  - [Índice](#índice)
  - [Requisitos do Sistema](#requisitos-do-sistema)
    - [Python e Dependências](#python-e-dependências)
    - [Dependências Python](#dependências-python)
  - [Instalação](#instalação)
  - [Configuração](#configuração)
    - [Banco de Dados](#banco-de-dados)
    - [Email](#email)
    - [Alertas](#alertas)
  - [Estrutura do Projeto](#estrutura-do-projeto)
  - [Executando o Sistema](#executando-o-sistema)
    - [1. Servidor de Usuários](#1-servidor-de-usuários)
    - [2. Gerador de Alertas](#2-gerador-de-alertas)
  - [Suporte](#suporte)
    - [Problemas Comuns](#problemas-comuns)

## Requisitos do Sistema

### Python e Dependências
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- bash (para execução dos scripts)

### Dependências Python
O arquivo `requirements.txt` contém todas as dependências necessárias. Instale-as usando:
```bash
pip install -r requirements.txt
```

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd cempa-notify
```

2. Crie e ative um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências do modulo_usuarios:
```bash
pip install -r ./modulo_usuarios/requirements.txt
```

4. Instale as dependencias do modulo_alertas:
```bash
sudo apt install pipx
pipx install poetry
pipx ensurepath
exec $SHELL
poetry install
```

## Configuração

### Banco de Dados
O sistema utiliza SQLite para armazenamento de dados:
- Localização: `modulo_usuarios/database/users.db`
- O banco é criado automaticamente na primeira execução
- Não é necessário configuração adicional

### Email
Para o envio de emails funcionar, configure uma senha de app do Gmail:

1. Acesse https://myaccount.google.com
2. Busque por "senhas de app" na barra de pesquisa
3. Gere uma senha de app para "CEMPA Notify"
4. Crie um arquivo `.env` na raiz do projeto:
```bash
touch .env  # Linux/Mac
# ou
type nul > .env  # Windows
```

5. Adicione as seguintes variáveis ao arquivo `.env`:
```env
EMAIL_APP_PASSWORD=sua_senha_de_app_aqui
EMAIL=seu_email@gmail.com
```

### Alertas
Os alertas são configurados em `config_files.csv`:
- Limiares de temperatura por cidade
- Limiares de umidade
- Períodos de monitoramento

Exemplo de configuração:
```csv
polygon_name,display_name,temp_max_jan,temp_max_feb,...
0230-Goiania,Goiânia,35,36,...
```

## Estrutura do Projeto

```
cempa-notify/
├── modulo_alertas/           # Módulo de geração e envio de alertas
│   ├── src/
│   │   ├── alert_generator.py    # Gerador principal de alertas
│   │   └── ...
├── modulo_usuarios/          # Módulo de gerenciamento de usuários
│   ├── src/
│   │   ├── models.py        # Modelos do banco de dados
│   │   ├── routes.py        # Rotas da API
│   │   └── ...
│   └── database/            # Banco de dados SQLite
├── config_files.csv         # Configurações de alertas
├── requirements.txt         # Dependências Python
.env                    # Configurações sensíveis
run_alertas.sh       # Script de execução
```

## Executando o Sistema

### 1. Servidor de Usuários
O servidor gerencia o cadastro de usuários e suas preferências de alerta:

```bash
cd modulo_usuarios
python -m src
```

- Porta padrão: 8081
- Acesse http://localhost:8081 para o formulário de cadastro
- API disponível em http://localhost:8081/users

### 2. Gerador de Alertas
O `alert_generator.py` é o componente principal que:
- Monitora condições meteorológicas
- Verifica limiares configurados
- Gera e envia alertas

Execute usando o script:
```bash
bash run_alertas.sh
```

O script:
- Ativa o ambiente virtual
- Executa o gerador de alertas
- Gerencia logs e erros

## Suporte

### Problemas Comuns

1. **Servidor não inicia**
   - Verifique se a porta 8081 está disponível
   - Confirme se o ambiente virtual está ativo
   - Verifique os logs do servidor

2. **Emails não são enviados**
   - Confirme se o arquivo `.env` existe e está configurado
   - Verifique se a senha de app está correta
   - Consulte os logs para detalhes do erro

3. **Alertas não são gerados**
   - Verifique `config_files.csv`
   - Confirme se o servidor de usuários está rodando
   - Consulte os logs do gerador de alertas
