FROM python:3.11-slim

WORKDIR /app

# Copia os requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do serviço
COPY . .

# O serviço de estoque roda o consumidor em primeiro plano
CMD ["python", "consumidor.py"]
