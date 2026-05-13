import pika
import json
import os
import sys

def publicar_evento_pagamento(dados, tipo_evento="sucesso"):
    """
    Publica um evento de pagamento (sucesso ou falha) no RabbitMQ.
    """
    try:
        usuario = os.getenv('RABBITMQ_USER', 'convidado')
        senha = os.getenv('RABBITMQ_PASS', 'convidado')
        host = os.getenv('RABBITMQ_HOST', 'rabbitmq')

        credenciais = pika.PlainCredentials(usuario, senha)
        parametros = pika.ConnectionParameters(host=host, credentials=credenciais)
        conexao = pika.BlockingConnection(parametros)
        canal = conexao.channel()

        # Usamos um fanout para que múltiplos serviços (Estoque, Pedidos, Notificações) 
        # ouçam o resultado do pagamento simultaneamente.
        exchange_nome = 'pagamento_ex'
        canal.exchange_declare(exchange=exchange_nome, exchange_type='fanout', durable=True)

        # Adicionamos o tipo de evento no payload
        dados["tipo_evento"] = tipo_evento
        mensagem = json.dumps(dados)

        canal.basic_publish(
            exchange=exchange_nome,
            routing_key='',
            body=mensagem,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        print(f" [MQ] Evento '{tipo_evento}' publicado para o Pedido #{dados.get('id_pedido')}")
        sys.stdout.flush()
        conexao.close()
    except Exception as e:
        print(f" [MQ-ERROR] Falha ao publicar evento: {e}")
        sys.stdout.flush()

def publicar_pagamento_sucesso(dados):
    publicar_evento_pagamento(dados, tipo_evento="sucesso")

def publicar_pagamento_falha(dados):
    publicar_evento_pagamento(dados, tipo_evento="falha")
