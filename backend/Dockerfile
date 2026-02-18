FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copia pyproject.toml primeiro para cache de deps
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Copia o código
COPY . .

# Cria diretório de dados
RUN mkdir -p /app/data

EXPOSE 8000

# Comando padrão: API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
