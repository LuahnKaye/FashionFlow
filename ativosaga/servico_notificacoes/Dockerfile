FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Consumidores não expõem porta, apenas ouvem o RabbitMQ
CMD ["python", "consumidor.py"]
