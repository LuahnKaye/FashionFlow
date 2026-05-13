FROM python:3.11-slim

WORKDIR /app

# Copia os requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do serviço
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Comando para rodar a API (que inicia o consumidor em background)
CMD ["uvicorn", "main:aplicativo_fastapi", "--host", "0.0.0.0", "--port", "8000"]
