import pika
import json
import time
import os
import sys
from banco_de_dados import SessaoLocal, motor_do_banco, Base
from modelos import Estoque
from utilitarios_rabbitmq import configurar_resiliencia

Base.metadata.create_all(bind=motor_do_banco)

def processar_pedido_criado(canal, metodo, propriedades, corpo):
    """Reserva o item no estoque quando o pedido nasce."""
    try:
        dados = json.loads(corpo)
        id_pedido = dados.get("id_pedido")
        id_produto = dados.get("id_produto")
        quantidade = dados.get("quantidade")

        banco = SessaoLocal()
        item = banco.query(Estoque).filter(Estoque.id_produto == id_produto).first()

        if item and item.quantidade_disponivel >= quantidade:
            item.quantidade_disponivel -= quantidade
            item.quantidade_reservada += quantidade
            banco.commit()
            print(f" ✅ [ESTOQUE] Reserva OK: Pedido #{id_pedido}")
            canal.basic_ack(delivery_tag=metodo.delivery_tag)
        else:
            print(f" ❌ [ESTOQUE] Sem saldo para Pedido #{id_pedido}")
            canal.basic_nack(delivery_tag=metodo.delivery_tag, requeue=False)
        banco.close()
    except Exception as e:
        print(f" 🔥 Erro reserva: {e}")
        canal.basic_nack(delivery_tag=metodo.delivery_tag, requeue=False)

def processar_resultado_pagamento(canal, metodo, propriedades, corpo):
    """Confirma a baixa ou devolve o estoque baseado no resultado do pagamento."""
    try:
        dados = json.loads(corpo)
        tipo = dados.get("tipo_evento")
        id_produto = dados.get("id_produto")
        quantidade = dados.get("quantidade", 1)

        banco = SessaoLocal()
        item = banco.query(Estoque).filter(Estoque.id_produto == id_produto).first()

        if not item:
            canal.basic_ack(delivery_tag=metodo.delivery_tag)
            return

        if tipo == "sucesso":
            # Pagamento OK: O item sai do 'reservado' definitivamente
            item.quantidade_reservada -= quantidade
            print(f" 📦 [ESTOQUE] Baixa definitiva: Produto #{id_produto}")
        elif tipo == "falha":
            # Pagamento Falhou: O item volta para o 'disponivel'
            item.quantidade_reservada -= quantidade
            item.quantidade_disponivel += quantidade
            print(f" ♻️ [ESTOQUE] Devolução (Saga Compensação): Produto #{id_produto}")

        banco.commit()
        banco.close()
        canal.basic_ack(delivery_tag=metodo.delivery_tag)
    except Exception as e:
        print(f" 🔥 Erro compensação: {e}")
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
            
            # 1. Escuta Pedidos Novos para Reservar
            configurar_resiliencia(canal, 'pedido.criado', 'pedido_ex', 'direct')
            canal.basic_consume(queue='pedido.criado', on_message_callback=processar_pedido_criado)

            # 2. Escuta Resultados de Pagamento para Confirmar ou Devolver
            configurar_resiliencia(canal, 'estoque.pagamento_sync', 'pagamento_ex', 'fanout')
            canal.basic_consume(queue='estoque.pagamento_sync', on_message_callback=processar_resultado_pagamento)
            
            print(" [READY] Estoque pronto (Reserva + Compensação).")
            sys.stdout.flush()
            canal.start_consuming()
        except Exception as e:
            print(f" [RETRY] Erro no Estoque: {e}. Reiniciando em 5s...")
            time.sleep(5)

if __name__ == "__main__":
    iniciar_consumidor()
