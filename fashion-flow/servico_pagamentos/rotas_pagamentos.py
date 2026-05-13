# pyrefly: ignore [missing-import]
import stripe
import os
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from banco_de_dados import obter_banco
from modelos import Transacao
from mensageria import publicar_pagamento_sucesso, publicar_pagamento_falha
from seguranca import verificar_token_acesso

# Configuração do Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

roteador = APIRouter()

@roteador.post("/teste-sucesso")
def disparar_sucesso_manual(id_pedido: int, id_usuario: int, id_produto: int):
    """Rota de debug para forçar o sucesso e testar a Saga."""
    publicar_pagamento_sucesso({
        "id_pedido": id_pedido,
        "id_usuario": id_usuario,
        "id_produto": id_produto,
        "valor": 99.90
    })
    return {"status": "Sinal de sucesso enviado para a Saga!"}

@roteador.get("/criar-sessao-pagamento/{id_pedido}")
def criar_sessao_pagamento(
    id_pedido: int, 
    banco: Session = Depends(obter_banco),
    dados_token: dict = Depends(verificar_token_acesso)
):
    """
    Cria uma sessão de checkout no Stripe para um pedido específico.
    """
    id_usuario = dados_token.get("id_usuario")
    
    try:
        # Criamos a sessão de checkout no Stripe
        sessao = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': f'Pedido #{id_pedido}',
                    },
                    'unit_amount': 9990, # R$ 99.90 em centavos
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:3000/sucesso?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:3000/cancelado',
            metadata={
                'id_pedido': str(id_pedido),
                'id_usuario': str(id_usuario)
            }
        )
        
        # Registramos a transação como PENDENTE no nosso banco
        nova_transacao = Transacao(
            id_pedido=id_pedido,
            id_usuario=id_usuario,
            id_sessao_stripe=sessao.id,
            status="PENDENTE",
            valor=99.90
        )
        banco.add(nova_transacao)
        banco.commit()
        
        return {"url_pagamento": sessao.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@roteador.get("/confirmar-pagamento/{id_sessao}")
def confirmar_pagamento(id_sessao: str, banco: Session = Depends(obter_banco)):
    """
    Verifica o status de uma sessão de pagamento no Stripe.
    """
    try:
        sessao = stripe.checkout.Session.retrieve(id_sessao)
        transacao = banco.query(Transacao).filter(Transacao.id_sessao_stripe == id_sessao).first()
        
        if not transacao:
            raise HTTPException(status_code=404, detail="Transação não encontrada.")
            
        if sessao.payment_status == 'paid':
            # IDEMPOTÊNCIA: Verificamos se já não processamos este pagamento anteriormente
            if transacao.status == "PAGO":
                return {"status": "PAGO", "mensagem": "Pagamento já havia sido processado."}

            transacao.status = "PAGO"
            banco.commit()
            
            # Notificamos os outros serviços sobre o sucesso
            publicar_pagamento_sucesso({
                "id_pedido": transacao.id_pedido,
                "id_usuario": transacao.id_usuario,
                "valor": transacao.valor
            })
            
            return {"status": "PAGO", "mensagem": "Pagamento confirmado com sucesso!"}
        
        return {"status": transacao.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@roteador.post("/webhook")
async def stripe_webhook(request: Request, banco: Session = Depends(obter_banco), stripe_signature: str = Header(None)):
    """
    Recebe notificações de eventos do Stripe (Webhooks).
    """
    payload = await request.body()
    
    try:
        evento = stripe.Webhook.construct_event(
            payload, stripe_signature, WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Assinatura do webhook invalida.")

    if evento['type'] == 'checkout.session.completed':
        sessao = evento['data']['object']
        metadata = sessao.get('metadata', {})
        id_pedido = metadata.get('id_pedido')
        
        transacao = banco.query(Transacao).filter(Transacao.id_sessao_stripe == sessao.id).first()
        if transacao:
            # IDEMPOTÊNCIA: Evita processar o mesmo webhook de sucesso duas vezes
            if transacao.status == "PAGO":
                return {"status": "sucesso", "detalhe": "Pagamento já processado anteriormente."}

            transacao.status = "PAGO"
            banco.commit()
            
            publicar_pagamento_sucesso({
                "id_pedido": int(id_pedido),
                "id_usuario": int(metadata.get('id_usuario')),
                "id_produto": int(metadata.get('id_produto', 0)),
                "valor": transacao.valor
            })
            
    elif evento['type'] in ['checkout.session.expired', 'payment_intent.payment_failed']:
        # Se o pagamento falhou ou expirou, disparamos a Saga de Compensação
        sessao = evento['data']['object']
        metadata = sessao.get('metadata', {})
        id_pedido = metadata.get('id_pedido')
        
        publicar_pagamento_falha({
            "id_pedido": int(id_pedido),
            "id_usuario": int(metadata.get('id_usuario'))
        })

    return {"status": "sucesso"}
