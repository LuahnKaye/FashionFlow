import pika
import json
import time
import os
import sys

def enviar_notificacao_email(canal, metodo, propriedades, corpo):
    """
    Simula o envio de um e-mail de confirmação para o usuário.
    """
    try:
        dados = json.loads(corpo)
        id_pedido = dados.get("id_pedido")
        id_usuario = dados.get("id_usuario")
        id_produto = dados.get("id_produto")
        valor = dados.get("valor")

        print(f"\n" + "="*50)
        print(f"📧 [NOTIFICAÇÕES] >>> ENVIANDO E-MAIL DE CONFIRMAÇÃO")
        print(f"="*50)
        print(f"Olá, Usuário #{id_usuario}!")
        print(f"Seu pagamento do Pedido #{id_pedido} foi confirmado.")
        print(f"Produto Digital: Ativo #{id_produto}")
        print(f"Valor Processado: R$ {valor:.2f}")
        print(f"O ativo já está disponível em sua Galeria FashionFlow.")
        print(f"="*50 + "\n")
        sys.stdout.flush()

        # Confirma o processamento da mensagem
        canal.basic_ack(delivery_tag=metodo.delivery_tag)
    except Exception as e:
        print(f" [ERRO] Falha ao processar notificação: {e}")
        sys.stdout.flush()

def iniciar_servico_notificacoes():
    """
    Configura o consumidor para o serviço de notificações.
    """
    usuario = os.getenv('RABBITMQ_USER', 'convidado')
    senha = os.getenv('RABBITMQ_PASS', 'convidado')
    host = os.getenv('RABBITMQ_HOST', 'rabbitmq')

    while True:
        try:
            print(f"[*] Notificações: Conectando em {host}...")
            sys.stdout.flush()
            
            credenciais = pika.PlainCredentials(usuario, senha)
            parametros = pika.ConnectionParameters(host=host, credentials=credenciais)
            conexao = pika.BlockingConnection(parametros)
            canal = conexao.channel()

            # Declaramos o Exchange (mesmo do pagamento)
            canal.exchange_declare(exchange='pagamento_ex', exchange_type='fanout', durable=True)
            
            # Criamos uma fila EXCLUSIVA para este serviço
            canal.queue_declare(queue='notificacoes.pagamento', durable=True)
            
            # Vinculamos a fila ao Exchange
            canal.queue_bind(exchange='pagamento_ex', queue='notificacoes.pagamento')

            canal.basic_qos(prefetch_count=1)
            canal.basic_consume(
                queue='notificacoes.pagamento',
                on_message_callback=enviar_notificacao_email
            )

            print(" [READY] Serviço de Notificações aguardando eventos...")
            sys.stdout.flush()
            canal.start_consuming()

        except Exception as e:
            print(f" [RETRY] Falha no serviço de notificações: {e}. Tentando em 5s...")
            sys.stdout.flush()
            time.sleep(5)

if __name__ == "__main__":
    iniciar_servico_notificacoes()
