import pika
import json
import os

def publicar_pagamento_sucesso(dados_pagamento):
    """
    Publica uma mensagem no RabbitMQ informando que o pagamento foi concluido.
    """
    try:
        usuario = os.getenv('RABBITMQ_USER', 'convidado')
        senha = os.getenv('RABBITMQ_PASS', 'convidado')
        host = os.getenv('RABBITMQ_HOST', 'rabbitmq')

        print(f"\n[MQ-DEBUG] Tentando conexão: {host} | Usuário: {usuario}")

        credenciais = pika.PlainCredentials(usuario, senha)
        parametros = pika.ConnectionParameters(
            host=host, 
            port=5672,
            credentials=credenciais
        )
        
        conexao = pika.BlockingConnection(parametros)
        canal = conexao.channel()

        canal.exchange_declare(exchange='pagamento_ex', exchange_type='fanout', durable=True)

        mensagem = json.dumps(dados_pagamento)
        canal.basic_publish(
            exchange='pagamento_ex',
            routing_key='',
            body=mensagem
        )
        print(f"[MQ-SUCCESS] Mensagem enviada para o Exchange!")
        conexao.close()
    except Exception as e:
        print(f"[MQ-ERROR] Falha crítica: {e}")
