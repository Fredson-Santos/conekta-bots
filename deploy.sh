#!/bin/bash
set -e  # Para o script se algum comando falhar

echo "🚀 Iniciando deploy..."

# Para os containers atuais
echo "⏹️  Parando containers..."
docker compose down

# Rebuild das imagens (força reconstrução para pegar código novo)
echo "🔨 Reconstruindo imagens..."
docker compose build --no-cache

# Sobe os containers
echo "▶️  Iniciando containers..."
docker compose up -d

# Aguarda alguns segundos para containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 5

# Mostra status
echo "📊 Status dos containers:"
docker compose ps

echo "✅ Deploy concluído!"
