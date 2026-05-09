import pika
import json
import time
import os
import sys
from banco_de_dados import SessaoLocal, motor_do_banco, Base
from modelos import BibliotecaUsuario

# Forçamos a criação das tabelas no início
print("[DB] Garantindo que as tabelas existem...")
Base.metadata.create_all(bind=motor_do_banco)

CATALOGO_IMAGENS = {
    501: "/imagens/produto_501_alta_resolucao.jpg",
    502: "/imagens/produto_502_alta_resolucao.jpg",
    503: "/imagens/produto_503_alta_resolucao.jpg",
}

def processar_pagamento_sucesso(canal, metodo, propriedades, corpo):
    print(f"\n>>> [ATIVOS] MENSAGEM RECEBIDA: {corpo.decode()}")
    sys.stdout.flush()
    
    try:
        dados = json.loads(corpo)
        id_pedido = dados.get("id_pedido")
        id_usuario = dados.get("id_usuario")
        id_produto = dados.get("id_produto")

        print(f"    [PROCESSANDO] Pedido #{id_pedido} para Usuário {id_usuario}")
        sys.stdout.flush()

        banco = SessaoLocal()
        url_imagem = CATALOGO_IMAGENS.get(id_produto, "/imagens/produto_generico.jpg")

        novo_ativo = BibliotecaUsuario(
            id_usuario=id_usuario,
            id_pedido=id_pedido,
            id_produto=id_produto,
            url_imagem=url_imagem,
            status="LIBERADO"
        )
        banco.add(novo_ativo)
        banco.commit()
        banco.close()

        print(f"    [SUCESSO] Ativo gravado no banco de dados!")
        sys.stdout.flush()
        
        canal.basic_ack(delivery_tag=metodo.delivery_tag)

    except Exception as e:
        print(f"    [ERRO CRÍTICO] Falha ao processar: {e}")
        sys.stdout.flush()
        # Se deu erro, não damos ACK para tentar de novo depois
        canal.basic_nack(delivery_tag=metodo.delivery_tag, requeue=True)

def iniciar_consumidor():
    usuario = os.getenv('RABBITMQ_USER', 'convidado')
    senha = os.getenv('RABBITMQ_PASS', 'convidado')
    host = os.getenv('RABBITMQ_HOST', 'rabbitmq')

    while True:
        try:
            print(f"[*] Ativos: Tentando conectar em {host}...")
            sys.stdout.flush()
            
            credenciais = pika.PlainCredentials(usuario, senha)
            parametros = pika.ConnectionParameters(
                host=host, 
                credentials=credenciais,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            conexao = pika.BlockingConnection(parametros)
            canal = conexao.channel()

            canal.exchange_declare(exchange='pagamento_ex', exchange_type='fanout', durable=True)
            canal.queue_declare(queue='pagamento.sucesso.v2', durable=True)
            canal.queue_bind(exchange='pagamento_ex', queue='pagamento.sucesso.v2')

            canal.basic_qos(prefetch_count=1)
            canal.basic_consume(queue='pagamento.sucesso.v2', on_message_callback=processar_pagamento_sucesso)

            print(" [READY] Consumidor de Ativos pronto e ouvindo!")
            sys.stdout.flush()
            canal.start_consuming()

        except Exception as e:
            print(f" [RETRY] Conexão caiu: {e}. Reiniciando em 5s...")
            sys.stdout.flush()
            time.sleep(5)

if __name__ == "__main__":
    iniciar_consumidor()
