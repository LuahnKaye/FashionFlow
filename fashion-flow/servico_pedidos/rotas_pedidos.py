# pyrefly: ignore [missing-import]
import pika
import json
import os
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from banco_de_dados import obter_banco
from modelos import Pedido
from esquemas import PedidoCriar, PedidoResposta
from seguranca import verificar_token_acesso

roteador = APIRouter(prefix="/pedidos", tags=["Pedidos"])

def enviar_mensagem_fila(dados_pedido: dict):
    """
    Envia uma mensagem para o RabbitMQ. Retorna True se tiver sucesso.
    """
    try:
        credenciais = pika.PlainCredentials(
            os.getenv('RABBITMQ_USER', 'convidado'), 
            os.getenv('RABBITMQ_PASS', 'convidado')
        )
        parametros = pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'localhost'), credentials=credenciais)
        conexao = pika.BlockingConnection(parametros)
        canal = conexao.channel()
        
        canal.exchange_declare(exchange='pedido_ex', exchange_type='direct', durable=True)
        
        canal.basic_publish(
            exchange='pedido_ex',
            routing_key='pedido.criado',
            body=json.dumps(dados_pedido),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        conexao.close()
        return True
    except Exception as e:
        print(f"Erro ao conectar ao RabbitMQ: {e}")
        return False

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
    
    # Criamos a entidade no banco, mas ainda não damos o commit final
    novo_pedido = Pedido(
        id_usuario=id_usuario,
        id_produto=pedido_entrada.id_produto,
        quantidade=pedido_entrada.quantidade,
        preco_total=pedido_entrada.preco_total,
        status="AGUARDANDO_RESERVA" # Começamos com um status intermediário
    )
    
    banco.add(novo_pedido)
    banco.flush() # Gera o ID do pedido sem salvar definitivamente
    
    # Preparamos os dados para a fila
    payload_fila = {
        "id_pedido": novo_pedido.id,
        "id_usuario": id_usuario,
        "id_produto": novo_pedido.id_produto,
        "quantidade": novo_pedido.quantidade
    }
    
    # Só confirmamos no banco se a mensagem foi para o RabbitMQ
    # Nota Técnica: Para um sistema de escala real, aqui usaríamos o 'Outbox Pattern'
    if enviar_mensagem_fila(payload_fila):
        novo_pedido.status = "PENDENTE"
        banco.commit()
        banco.refresh(novo_pedido)
        return novo_pedido
    else:
        banco.rollback()
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Sistema de mensageria indisponível. Tente novamente em instantes.")
