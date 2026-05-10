import pika
import json
import time
import os
import sys
from utilitarios_rabbitmq import configurar_resiliencia

def enviar_notificacao_email(canal, metodo, propriedades, corpo):
    """
    Simula o envio de um e-mail de confirmação.
    """
    try:
        dados = json.loads(corpo)
        id_pedido = dados.get("id_pedido")
        id_usuario = dados.get("id_usuario")

        # SIMULAÇÃO DE ERRO: Se for o usuário #999, o sistema "falha" para testarmos a DLQ
        if id_usuario == 999:
            raise Exception("Falha simulada no envio de e-mail crítico!")

        print(f"\n📧 [NOTIFICAÇÕES] >>> Enviando e-mail para Usuário #{id_usuario} (Pedido #{id_pedido})")
        sys.stdout.flush()

        canal.basic_ack(delivery_tag=metodo.delivery_tag)
    except Exception as e:
        print(f" [ERRO-DLQ] Enviando mensagem para a UTI (DLQ): {e}")
        sys.stdout.flush()
        # Nack com requeue=False joga a mensagem direto para a DLQ configurada
        canal.basic_nack(delivery_tag=metodo.delivery_tag, requeue=False)

def iniciar_servico_notificacoes():
    usuario = os.getenv('RABBITMQ_USER', 'convidado')
    senha = os.getenv('RABBITMQ_PASS', 'convidado')
    host = os.getenv('RABBITMQ_HOST', 'rabbitmq')

    while True:
        try:
            credenciais = pika.PlainCredentials(usuario, senha)
            parametros = pika.ConnectionParameters(host=host, credentials=credenciais)
            conexao = pika.BlockingConnection(parametros)
            canal = conexao.channel()

            # Usamos o utilitário para configurar a fila com DLQ
            configurar_resiliencia(
                canal=canal, 
                nome_da_fila='notificacoes.pagamento', 
                exchange_principal='pagamento_ex'
            )

            canal.basic_qos(prefetch_count=1)
            canal.basic_consume(
                queue='notificacoes.pagamento',
                on_message_callback=enviar_notificacao_email
            )

            print(" [READY] Notificações protegidas com DLQ prontas.")
            sys.stdout.flush()
            canal.start_consuming()

        except Exception as e:
            print(f" [RETRY] Erro: {e}. Tentando em 5s...")
            sys.stdout.flush()
            time.sleep(5)

if __name__ == "__main__":
    iniciar_servico_notificacoes()
