import pika
import json
import time
import os
import sys
from banco_de_dados import SessaoLocal, motor_do_banco, Base
from modelos import Pedido
from utilitarios_rabbitmq import configurar_resiliencia

Base.metadata.create_all(bind=motor_do_banco)

def processar_resultado_pagamento(canal, metodo, propriedades, corpo):
    """Atualiza o status do pedido baseado no sucesso ou falha do pagamento."""
    try:
        dados = json.loads(corpo)
        id_pedido = dados.get("id_pedido")
        tipo = dados.get("tipo_evento")

        banco = SessaoLocal()
        pedido = banco.query(Pedido).filter(Pedido.id == id_pedido).first()

        if pedido:
            if tipo == "sucesso":
                pedido.status = "PAGO"
                print(f" ✅ [PEDIDOS] Pedido #{id_pedido} confirmado como PAGO.")
            elif tipo == "falha":
                pedido.status = "CANCELADO"
                print(f" ❌ [PEDIDOS] Pedido #{id_pedido} marcado como CANCELADO (Falha no Pagamento).")
            
            banco.commit()
            canal.basic_ack(delivery_tag=metodo.delivery_tag)
        else:
            print(f" ⚠️ [PEDIDOS] Pedido #{id_pedido} não encontrado para sincronização.")
            canal.basic_ack(delivery_tag=metodo.delivery_tag)

        banco.close()
    except Exception as e:
        print(f" 🔥 Erro sincronização de pedidos: {e}")
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
            
            configurar_resiliencia(canal, 'pagamentos.pedidos_sync', 'pagamento_ex', 'fanout')

            canal.basic_qos(prefetch_count=1)
            canal.basic_consume(queue='pagamentos.pedidos_sync', on_message_callback=processar_resultado_pagamento)
            
            print(" [READY] Sincronizador de Pedidos pronto (Sucesso + Cancelamento).")
            sys.stdout.flush()
            canal.start_consuming()
            
        except Exception as e:
            print(f" [RETRY] Erro no Pedidos: {e}. Reiniciando em 5s...")
            time.sleep(5)

if __name__ == "__main__":
    iniciar_consumidor()
