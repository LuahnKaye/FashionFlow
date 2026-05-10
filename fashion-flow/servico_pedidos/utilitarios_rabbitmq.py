import pika
import os
import sys
import time

def configurar_resiliencia(canal, nome_da_fila, exchange_principal, tipo_exchange='fanout'):
    """
    Configura uma fila com Dead Letter Exchange (DLX).
    Se a mensagem falhar ou expirar, ela vai para a fila de 'morte'.
    """
    # 1. Declaramos o Exchange de "Mensagens Mortas" (A UTI)
    dlx_name = f"dlx.{exchange_principal}"
    canal.exchange_declare(exchange=dlx_name, exchange_type='direct', durable=True)

    # 2. Declaramos a Fila de "Mensagens Mortas"
    dlq_name = f"dlq.{nome_da_fila}"
    canal.queue_declare(queue=dlq_name, durable=True)
    canal.queue_bind(exchange=dlx_name, queue=dlq_name, routing_key="mortas")

    # 3. Declaramos a Fila Principal com as configurações de redirecionamento para a DLX
    argumentos = {
        'x-dead-letter-exchange': dlx_name,
        'x-dead-letter-routing-key': 'mortas',
        'x-message-ttl': 30000 # 30 segundos de vida antes de ir para a DLQ se ninguém processar
    }

    canal.exchange_declare(exchange=exchange_principal, exchange_type=tipo_exchange, durable=True)
    canal.queue_declare(queue=nome_da_fila, durable=True, arguments=argumentos)
    canal.queue_bind(exchange=exchange_principal, queue=nome_da_fila)

    print(f" [RESILIÊNCIA] Fila '{nome_da_fila}' protegida por DLX '{dlx_name}'")
    sys.stdout.flush()
