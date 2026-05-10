import pika
import json
import time
import os
import sys
from banco_de_dados import SessaoLocal, motor_do_banco, Base
from modelos import BibliotecaUsuario
from utilitarios_rabbitmq import configurar_resiliencia

# Forçamos a criação das tabelas
Base.metadata.create_all(bind=motor_do_banco)

CATALOGO_IMAGENS = {
    501: "/imagens/produto_501_alta_resolucao.jpg",
    502: "/imagens/produto_502_alta_resolucao.jpg",
    503: "/imagens/produto_503_alta_resolucao.jpg",
}

def processar_pagamento_sucesso(canal, metodo, propriedades, corpo):
    try:
        dados = json.loads(corpo)
        id_pedido = dados.get("id_pedido")
        id_usuario = dados.get("id_usuario")
        id_produto = dados.get("id_produto")

        print(f"\n [PROCESSANDO] Pedido #{id_pedido} para Usuário {id_usuario}")
        sys.stdout.flush()

        banco = SessaoLocal()
        
        # IDEMPOTÊNCIA: Verificamos se esse pedido já não foi processado antes
        existente = banco.query(BibliotecaUsuario).filter(BibliotecaUsuario.id_pedido == id_pedido).first()
        if existente:
            print(f"  [IGNORANDO] Pedido #{id_pedido} já foi entregue anteriormente.")
            canal.basic_ack(delivery_tag=metodo.delivery_tag)
            banco.close()
            return

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

        print(f"  ✅ [SUCESSO] Ativo liberado na galeria!")
        sys.stdout.flush()
        canal.basic_ack(delivery_tag=metodo.delivery_tag)

    except Exception as e:
        print(f"  🔥 [ERRO-DLQ] Falha no processamento de ativos: {e}")
        sys.stdout.flush()
        # Envia para a DLQ em caso de falha persistente
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
                nome_da_fila='pagamento.sucesso.v2',
                exchange_principal='pagamento_ex'
            )

            canal.basic_qos(prefetch_count=1)
            canal.basic_consume(queue='pagamento.sucesso.v2', on_message_callback=processar_pagamento_sucesso)

            print(" [READY] Serviço de Ativos pronto com proteção DLQ.")
            sys.stdout.flush()
            canal.start_consuming()

        except Exception as e:
            print(f" [RETRY] Erro: {e}. Reiniciando em 5s...")
            sys.stdout.flush()
            time.sleep(5)

if __name__ == "__main__":
    iniciar_consumidor()
