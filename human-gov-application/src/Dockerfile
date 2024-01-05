# Utilize o Python como imagem base
FROM python:3.8-slim-buster

# Configure o diretório de trabalho
WORKDIR /app

# Copie os requisitos e instale as dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie a aplicação Flask
COPY . /app

# Inicie o Gunicorn
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8000", "humangov:app"]
