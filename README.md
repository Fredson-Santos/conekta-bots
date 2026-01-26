# ConektaBots

ConektaBots é uma plataforma para gerenciamento e automação de bots do Telegram, com interface web para administração de bots, regras de encaminhamento, agendamentos e monitoramento de execuções.

## Funcionalidades
- Cadastro e gerenciamento de múltiplos bots do Telegram (userbot ou bot API)
- Criação de regras de encaminhamento entre canais/grupos
- Agendamento de tarefas
- Logs de execução e monitoramento
- Interface web com FastAPI e Jinja2

## Estrutura do Projeto
```
adicionar_bot.py         # Script CLI para adicionar bots ao banco
adicionar_regra.py       # Script CLI para adicionar regras de encaminhamento
app.py                   # API e interface web (FastAPI)
database.py              # Modelos e conexão com banco de dados (SQLModel)
manager.py               # Gerenciador principal: inicia todos os bots ativos
populardb.py             # Script para popular o banco com dados de exemplo
worker.py                # Worker assíncrono que executa os bots e regras
requirements.txt         # Dependências do projeto
bots/                    # (Pasta reservada para arquivos de bots)
templates/               # Templates HTML (Jinja2)
```

## Como rodar o projeto

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure o banco de dados:**
   O projeto utiliza SQLite por padrão. Os modelos são criados automaticamente ao rodar os scripts.

3. **Adicione um bot:**
   ```bash
   python adicionar_bot.py
   ```
   Siga as instruções para cadastrar um bot (userbot ou bot API).

4. **Adicione regras de encaminhamento:**
   ```bash
   python adicionar_regra.py
   ```

5. **Inicie o sistema de bots:**
   ```bash
   python manager.py
   ```

6. **(Opcional) Rode a interface web:**
   ```bash
   uvicorn app:app --reload
   ```
   Acesse: http://localhost:8000

## Principais Tecnologias
- Python 3.10+
- FastAPI
- SQLModel
- Telethon
- Jinja2

## Observações
- O arquivo `populardb.py` pode ser usado para inserir dados de exemplo no banco.
- Os templates HTML estão na pasta `templates/`.
- O projeto é modular e pode ser expandido para novas funcionalidades.

---

Desenvolvido por [Seu Nome].