#!/bin/bash
set -e  # Para o script se algum comando falhar

echo "🚀 Iniciando deploy..."

# Para e remove containers atuais (incluindo órfãos)
echo "⏹️  Parando e removendo containers antigos..."
docker compose down --remove-orphans || true

# Remove containers órfãos manualmente (fallback)
echo "🧹 Limpando containers órfãos..."
docker rm -f conekta_web conekta_manager 2>/dev/null || true

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

