# pyrefly: ignore [missing-import]
import pika
import json
import os
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from banco_de_dados import obter_banco
from modelos import Pedido
from esquemas import PedidoCriar, PedidoResposta
from seguranca import verificar_token_acesso

roteador = APIRouter(prefix="/pedidos", tags=["Pedidos"])

def enviar_mensagem_fila(dados_pedido: dict):
    """
    Envia uma mensagem para o RabbitMQ notificando a criação do pedido.
    """
    try:
        credenciais = pika.PlainCredentials(
            os.getenv('RABBITMQ_USER', 'convidado'), 
            os.getenv('RABBITMQ_PASS', 'convidado')
        )
        parametros = pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'localhost'), credentials=credenciais)
        conexao = pika.BlockingConnection(parametros)
        canal = conexao.channel()
        
        # Garantimos que a fila existe
        canal.queue_declare(queue='pedido.criado', durable=True)
        
        # Publicamos a mensagem
        canal.basic_publish(
            exchange='',
            routing_key='pedido.criado',
            body=json.dumps(dados_pedido),
            properties=pika.BasicProperties(delivery_mode=2) # Torna a mensagem persistente
        )
        conexao.close()
    except Exception as e:
        print(f"Erro ao conectar ao RabbitMQ: {e}")
        # Em produção, poderíamos usar uma estratégia de retry aqui

@roteador.post("/", response_model=PedidoResposta)
def criar_pedido(
    pedido_entrada: PedidoCriar, 
    banco: Session = Depends(obter_banco),
    dados_token: dict = Depends(verificar_token_acesso)
):
    """
    Registra um novo pedido e notifica o sistema via mensageria.
    """
    id_usuario = dados_token.get("id_usuario")
    
    # Criamos a entidade no banco
    novo_pedido = Pedido(
        id_usuario=id_usuario,
        id_produto=pedido_entrada.id_produto,
        quantidade=pedido_entrada.quantidade,
        preco_total=pedido_entrada.preco_total,
        status="PENDENTE"
    )
    
    banco.add(novo_pedido)
    banco.commit()
    banco.refresh(novo_pedido)
    
    # Preparamos os dados para a fila (id do pedido, id do usuario e o que foi comprado)
    payload_fila = {
        "id_pedido": novo_pedido.id,
        "id_usuario": id_usuario,
        "id_produto": novo_pedido.id_produto,
        "quantidade": novo_pedido.quantidade
    }
    
    # Notificamos os outros serviços (como o Estoque)
    enviar_mensagem_fila(payload_fila)
    
    return novo_pedido
