# Usa uma versão leve do Python
FROM python:3.10-slim

# Configurações para Python rodar melhor em container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema (necessário para compilar algumas libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código para dentro da imagem
COPY . .

# Informa que a porta 8000 será usada
EXPOSE 8000