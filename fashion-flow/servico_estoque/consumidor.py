import pika
import json
import time
from sqlalchemy.orm import Session
from banco_de_dados import SessaoLocal, motor_do_banco, Base
from modelos import Estoque

# Garantimos que a tabela existe antes do consumidor rodar
Base.metadata.create_all(bind=motor_do_banco)

def processar_pedido_criado(canal, metodo, propriedades, corpo):
    """
    Callback executado quando uma mensagem chega na fila 'pedido.criado'.
    """
    dados = json.loads(corpo)
    id_pedido = dados.get("id_pedido")
    id_produto = dados.get("id_produto")
    quantidade = dados.get("quantidade")

    print(f"\n[x] Processando Pedido #{id_pedido} | Produto: {id_produto} | Qtd: {quantidade}")

    banco = SessaoLocal()
    try:
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
            # Em um sistema real, aqui dispararíamos uma mensagem 'estoque.insuficiente'
            # para cancelar o pedido automaticamente.
            canal.basic_nack(delivery_tag=metodo.delivery_tag, requeue=False)

    except Exception as e:
        print(f"    🔥 Erro ao processar: {e}")
        banco.rollback()
    finally:
        banco.close()

def iniciar_consumidor():
    """
    Configura a conexão com o RabbitMQ e começa a ouvir a fila.
    """
    while True:
        try:
            credenciais = pika.PlainCredentials('convidado', 'convidado')
            parametros = pika.ConnectionParameters(host='localhost', credentials=credenciais)
            conexao = pika.BlockingConnection(parametros)
            canal = conexao.channel()
            
            canal.queue_declare(queue='pedido.criado', durable=True)
            
            # Dizemos ao RabbitMQ para não mandar mais de uma mensagem por vez para este trabalhador
            canal.basic_qos(prefetch_count=1)
            
            canal.basic_consume(queue='pedido.criado', on_message_callback=processar_pedido_criado)
            
            print(" [*] Aguardando mensagens da fila 'pedido.criado'. Para sair pressione CTRL+C")
            canal.start_consuming()
            
        except pika.exceptions.AMQPConnectionError:
            print(" [!] RabbitMQ nao encontrado. Tentando novamente em 5 segundos...")
            time.sleep(5)

if __name__ == "__main__":
    iniciar_consumidor()
