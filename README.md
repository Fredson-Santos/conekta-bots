# ConektaBots

> ⚠️ **Este projeto está em fase MVP (Produto Mínimo Viável) e em construção ativa.** Funcionalidades podem mudar e novas features estão sendo desenvolvidas.

ConektaBots é uma plataforma para gerenciamento e automação de bots do Telegram, com interface web para administração de bots, regras de encaminhamento, agendamentos e monitoramento de execuções.

## ✨ Funcionalidades
- 🤖 Cadastro e gerenciamento de múltiplos bots do Telegram (userbot ou bot API)
- 📨 Criação de regras de encaminhamento entre canais/grupos
- 🔍 Filtros avançados com Regex (blacklist e whitelist)
- ⏰ Agendamento de tarefas com horários flexíveis
- 📊 Logs de execução e monitoramento em tempo real
- 🌐 Interface web com FastAPI e Jinja2
- 🚀 Deploy automático via CI/CD (GitHub Actions)

## 📁 Estrutura do Projeto
```
adicionar_bot.py         # Script CLI para adicionar bots ao banco
adicionar_regra.py       # Script CLI para adicionar regras de encaminhamento
app.py                   # API e interface web (FastAPI)
database.py              # Modelos e conexão com banco de dados (SQLModel)
manager.py               # Gerenciador principal: inicia todos os bots ativos
worker.py                # Worker assíncrono que executa os bots e regras
deploy.sh                # Script de deploy automático
requirements.txt         # Dependências do projeto (versões fixadas)
templates/               # Templates HTML (Jinja2)
```

## 🚀 Como rodar o projeto

### Opção 1: Docker (Recomendado)

```bash
docker-compose up -d --build
```

Acesse o painel: **http://localhost:5005**

### Opção 2: Manual

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Adicione um bot:**
   ```bash
   python adicionar_bot.py
   ```

3. **Adicione regras de encaminhamento:**
   ```bash
   python adicionar_regra.py
   ```

4. **Inicie o sistema de bots:**
   ```bash
   python manager.py
   ```

5. **(Opcional) Rode a interface web:**
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 5005
   ```

## 🐳 Docker Compose

O projeto roda em **2 serviços**:

| Serviço | Função | Porta |
|---|---|---|
| `web` | Painel de administração FastAPI | 5005 |
| `manager` | Gerenciador que executa os bots | - |

**Observação:** A porta 5005 é usada para o Cloudflare Tunnel.

## 🛠 Principais Tecnologias

- Python 3.10+
- FastAPI + Jinja2
- SQLModel (SQLite)
- Telethon
- Docker + Docker Compose

## 📝 Observações

- O banco de dados SQLite (`database.db`) é criado automaticamente na primeira execução
- Os templates HTML estão na pasta `templates/`
- O projeto é modular e pode ser expandido para novas funcionalidades
- Todas as dependências estão com versões fixadas para garantir estabilidade 