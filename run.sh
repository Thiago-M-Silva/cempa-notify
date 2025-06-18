#!/bin/bash

# Ir para o diretório do módulo alertas onde está o pyproject.toml
cd /home/suporte/cempa-notify/modulo_alertas

# Verificar arquivo .env em ambos os diretórios
if [ -f .env ]; then
    # Carregar variáveis do arquivo .env local
    set -a
    source .env
    set +a
    echo "Variáveis carregadas do arquivo .env local."
elif [ -f ../.env ]; then
    # Carregar variáveis do arquivo .env no diretório pai
    set -a
    source ../.env
    set +a
    echo "Variáveis carregadas do arquivo .env do diretório pai."
else
    echo "AVISO: Arquivo .env não encontrado em nenhum diretório!"
fi

# Registrar execução
echo "Executando script em $(date)"
echo "Diretório atual: $(pwd)"
echo "Variáveis de ambiente carregadas"

# Executar o script com Poetry a partir do diretório atual
/home/suporte/.local/bin/poetry run python3 src/alert_generator.py

# Registrar finalização
echo "Script finalizado em $(date) com código de saída $?"