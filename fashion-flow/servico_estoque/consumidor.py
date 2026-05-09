import pika
import json
import time
import os
import sys
from sqlalchemy.orm import Session
from banco_de_dados import SessaoLocal, motor_do_banco, Base
from modelos import Estoque

# Garantimos que a tabela existe antes do consumidor rodar
Base.metadata.create_all(bind=motor_do_banco)

def processar_pedido_criado(canal, metodo, propriedades, corpo):
    """
    Callback executado quando uma mensagem chega na fila 'pedido.criado'.
    """
    try:
        dados = json.loads(corpo)
        id_pedido = dados.get("id_pedido")
        id_produto = dados.get("id_produto")
        quantidade = dados.get("quantidade")

        print(f"\n[ESTOQUE] >>> Processando Pedido #{id_pedido} | Produto: {id_produto} | Qtd: {quantidade}")
        sys.stdout.flush()

        banco = SessaoLocal()
        # Buscamos o item no estoque
        item = banco.query(Estoque).filter(Estoque.id_produto == id_produto).first()

        if item and item.quantidade_disponivel >= quantidade:
            # Reservamos o item: tiramos do disponivel e colocamos no reservado
            item.quantidade_disponivel -= quantidade
            item.quantidade_reservada += quantidade
            banco.commit()
            print(f"    ✅ Sucesso: Estoque reservado para o Pedido #{id_pedido}")
            
            # Avisamos ao RabbitMQ que a mensagem foi processada com sucesso
            canal.basic_ack(delivery_tag=metodo.delivery_tag)
        else:
            print(f"    ❌ Falha: Estoque insuficiente para o Produto {id_produto}")
            # Em produção, aqui enviaríamos 'estoque.insuficiente'
            canal.basic_nack(delivery_tag=metodo.delivery_tag, requeue=False)

        banco.close()
    except Exception as e:
        print(f"    🔥 Erro ao processar: {e}")
        sys.stdout.flush()

def iniciar_consumidor():
    usuario = os.getenv('RABBITMQ_USER', 'convidado')
    senha = os.getenv('RABBITMQ_PASS', 'convidado')
    host = os.getenv('RABBITMQ_HOST', 'rabbitmq')

    while True:
        try:
            print(f"[*] Estoque: Conectando em {host}...")
            sys.stdout.flush()
            
            credenciais = pika.PlainCredentials(usuario, senha)
            parametros = pika.ConnectionParameters(host=host, credentials=credenciais)
            conexao = pika.BlockingConnection(parametros)
            canal = conexao.channel()
            
            canal.queue_declare(queue='pedido.criado', durable=True)
            canal.basic_qos(prefetch_count=1)
            canal.basic_consume(queue='pedido.criado', on_message_callback=processar_pedido_criado)
            
            print(" [READY] Estoque aguardando mensagens...")
            sys.stdout.flush()
            canal.start_consuming()
            
        except Exception as e:
            print(f" [RETRY] Erro de conexão: {e}. Tentando em 5s...")
            sys.stdout.flush()
            time.sleep(5)

if __name__ == "__main__":
    iniciar_consumidor()
