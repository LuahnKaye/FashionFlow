import pika
import json
import time
import os

def enviar_notificacao_email(canal, metodo, propriedades, corpo):
    """
    Simula o envio de um e-mail de confirmação para o usuário.
    """
    dados = json.loads(corpo)
    id_pedido = dados.get("id_pedido")
    id_usuario = dados.get("id_usuario")
    id_produto = dados.get("id_produto")
    valor = dados.get("valor")

    print(f"\n" + "="*50)
    print(f"📧 [EMAIL] NOTIFICAÇÃO DE COMPRA")
    print(f"="*50)
    print(f"Olá, Usuário #{id_usuario}!")
    print(f"Seu pagamento do Pedido #{id_pedido} foi confirmado.")
    print(f"Produto Digital: Ativo #{id_produto}")
    print(f"Valor Processado: R$ {valor:.2f}")
    print(f"O ativo já está disponível em sua Galeria FashionFlow.")
    print(f"="*50 + "\n")

    # Confirma o processamento da mensagem
    canal.basic_ack(delivery_tag=metodo.delivery_tag)

def iniciar_servico_notificacoes():
    """
    Configura o consumidor para o serviço de notificações.
    """
    while True:
        try:
            credenciais = pika.PlainCredentials(
                os.getenv('RABBITMQ_USER', 'convidado'), 
                os.getenv('RABBITMQ_PASS', 'convidado')
            )
            parametros = pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'localhost'), credentials=credenciais)
            conexao = pika.BlockingConnection(parametros)
            canal = conexao.channel()

            # Declaramos o Exchange (mesmo do pagamento)
            canal.exchange_declare(exchange='pagamento_ex', exchange_type='fanout', durable=True)
            
            # Criamos uma fila EXCLUSIVA para este serviço
            # Assim, Ativos e Notificações recebem a mesma mensagem de forma independente
            resultado = canal.queue_declare(queue='notificacoes.pagamento', durable=True)
            nome_da_fila = resultado.method.queue
            
            # Vinculamos a fila ao Exchange
            canal.queue_bind(exchange='pagamento_ex', queue=nome_da_fila)

            canal.basic_qos(prefetch_count=1)
            canal.basic_consume(
                queue=nome_da_fila,
                on_message_callback=enviar_notificacao_email
            )

            print(" [*] Serviço de Notificações iniciado. Aguardando eventos de pagamento...")
            canal.start_consuming()

        except pika.exceptions.AMQPConnectionError:
            print(" [!] RabbitMQ nao encontrado. Tentando novamente em 5 segundos...")
            time.sleep(5)
        except Exception as e:
            print(f" [ERRO] Falha no serviço de notificações: {e}")
            time.sleep(5)

if __name__ == "__main__":
    iniciar_servico_notificacoes()
