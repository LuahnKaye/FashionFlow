import pika
import json
import time
import os
import sys
from banco_de_dados import SessaoLocal, motor_do_banco, Base
from modelos import Pedido

# Garantimos que a tabela existe antes do consumidor rodar
Base.metadata.create_all(bind=motor_do_banco)

def processar_pagamento_sucesso(canal, metodo, propriedades, corpo):
    """
    Callback executado quando um pagamento é confirmado com sucesso.
    """
    try:
        dados = json.loads(corpo)
        id_pedido = dados.get("id_pedido")

        print(f"\n[PEDIDOS] >>> Atualizando status do Pedido #{id_pedido} para PAGO")
        sys.stdout.flush()

        banco = SessaoLocal()
        pedido = banco.query(Pedido).filter(Pedido.id == id_pedido).first()

        if pedido:
            pedido.status = "PAGO"
            banco.commit()
            print(f"    ✅ Sucesso: Pedido #{id_pedido} marcado como PAGO.")
            canal.basic_ack(delivery_tag=metodo.delivery_tag)
        else:
            print(f"    ⚠️ Aviso: Pedido #{id_pedido} não encontrado.")
            canal.basic_ack(delivery_tag=metodo.delivery_tag)

        banco.close()
    except Exception as e:
        print(f"    🔥 Erro ao atualizar pedido: {e}")
        sys.stdout.flush()

def iniciar_consumidor():
    usuario = os.getenv('RABBITMQ_USER', 'convidado')
    senha = os.getenv('RABBITMQ_PASS', 'convidado')
    host = os.getenv('RABBITMQ_HOST', 'rabbitmq')

    while True:
        try:
            print(f"[*] Pedidos: Conectando em {host}...")
            sys.stdout.flush()
            
            credenciais = pika.PlainCredentials(usuario, senha)
            parametros = pika.ConnectionParameters(host=host, credentials=credenciais)
            conexao = pika.BlockingConnection(parametros)
            canal = conexao.channel()
            
            canal.exchange_declare(exchange='pagamento_ex', exchange_type='fanout', durable=True)
            canal.queue_declare(queue='pagamentos.pedidos_sync', durable=True)
            canal.queue_bind(exchange='pagamento_ex', queue='pagamentos.pedidos_sync')

            canal.basic_qos(prefetch_count=1)
            canal.basic_consume(queue='pagamentos.pedidos_sync', on_message_callback=processar_pagamento_sucesso)
            
            print(" [READY] Sincronizador de Pedidos pronto!")
            sys.stdout.flush()
            canal.start_consuming()
            
        except Exception as e:
            print(f" [RETRY] Erro no Pedidos: {e}. Tentando em 5s...")
            sys.stdout.flush()
            time.sleep(5)

if __name__ == "__main__":
    iniciar_consumidor()
