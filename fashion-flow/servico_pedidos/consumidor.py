import pika
import json
import time
import os
import sys
from banco_de_dados import SessaoLocal, motor_do_banco, Base
from modelos import Pedido
from utilitarios_rabbitmq import configurar_resiliencia

# Garantimos que a tabela existe
Base.metadata.create_all(bind=motor_do_banco)

def processar_pagamento_sucesso(canal, metodo, propriedades, corpo):
    """
    Atualiza status do pedido com tratamento de erro e DLQ.
    """
    try:
        dados = json.loads(corpo)
        id_pedido = dados.get("id_pedido")

        banco = SessaoLocal()
        pedido = banco.query(Pedido).filter(Pedido.id == id_pedido).first()

        if pedido:
            pedido.status = "PAGO"
            banco.commit()
            print(f" ✅ [SYNC-PEDIDO] #{id_pedido} marcado como PAGO.")
            canal.basic_ack(delivery_tag=metodo.delivery_tag)
        else:
            # Se o pedido não existir, algo está muito errado nos dados. Vai para DLQ.
            print(f" ⚠️ [DLQ] Pedido #{id_pedido} não encontrado. Enviando para DLQ.")
            canal.basic_nack(delivery_tag=metodo.delivery_tag, requeue=False)

        banco.close()
    except Exception as e:
        print(f" 🔥 Erro crítico no Sync de Pedidos: {e}")
        sys.stdout.flush()
        canal.basic_nack(delivery_tag=metodo.delivery_tag, requeue=False)

def iniciar_consumidor():
    usuario = os.getenv('RABBITMQ_USER', 'convidado')
    senha = os.getenv('RABBITMQ_PASS', 'convidado')
    host = os.getenv('RABBITMQ_HOST', 'rabbitmq')

    while True:
        try:
            credenciais = pika.PlainCredentials(usuario, senha)
            parametros = pika.ConnectionParameters(host=host, credentials=credenciais)
            conexao = pika.BlockingConnection(parametros)
            canal = conexao.channel()
            
            configurar_resiliencia(
                canal=canal,
                nome_da_fila='pagamentos.pedidos_sync',
                exchange_principal='pagamento_ex'
            )

            canal.basic_qos(prefetch_count=1)
            canal.basic_consume(queue='pagamentos.pedidos_sync', on_message_callback=processar_pagamento_sucesso)
            
            print(" [READY] Sincronizador de Pedidos protegido com DLQ.")
            sys.stdout.flush()
            canal.start_consuming()
            
        except Exception as e:
            print(f" [RETRY] Erro no Pedidos: {e}. Tentando em 5s...")
            sys.stdout.flush()
            time.sleep(5)

if __name__ == "__main__":
    iniciar_consumidor()
