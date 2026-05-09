import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from banco_de_dados import obter_banco
from modelos import Transacao
from esquemas import PagamentoCriar, TransacaoResposta
from mensageria import publicar_pagamento_sucesso

import os

# --- CONFIGURAÇÃO DO STRIPE ---
STRIPE_CHAVE_SECRETA = os.getenv("STRIPE_SECRET_KEY", "chave_nao_configurada")
STRIPE_WEBHOOK_SECRETO = os.getenv("STRIPE_WEBHOOK_SECRET", "webhook_nao_configurado")

stripe.api_key = STRIPE_CHAVE_SECRETA

from seguranca import verificar_token_acesso

# ... (outros imports)

roteador = APIRouter()

# ========================
# ROTA 1: Criar Sessão de Checkout
# ========================
@roteador.post("/criar-checkout", response_model=TransacaoResposta)
def criar_sessao_checkout(
    pagamento: PagamentoCriar,
    banco: Session = Depends(obter_banco),
    dados_token: dict = Depends(verificar_token_acesso)
):
    """
    Cria uma Sessão de Checkout no Stripe garantindo a identidade do usuário via JWT.
    """
    # SEGURANÇA: Usamos o ID do token, NAO o que vem do corpo da requisicao (frontend)
    id_usuario_seguro = dados_token.get("id_usuario")
    """
    Cria uma Sessão de Checkout no Stripe e registra a transação localmente.

    O frontend receberá a URL e redirecionará o usuário para a página
    de pagamento hospedada pelo próprio Stripe.

    Args:
        pagamento (PagamentoCriar): Dados do pedido e valor.
        banco (Session): Sessão ativa com o banco de dados.

    Returns:
        TransacaoResposta: Dados da transação incluindo a URL de checkout.
    """
    try:
        # O Stripe trabalha com centavos, então multiplicamos por 100
        sessao = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "brl",
                    "product_data": {
                        "name": pagamento.nome_produto,
                    },
                    "unit_amount": int(pagamento.valor * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            # URLs para onde o Stripe redireciona o usuário após o pagamento
            success_url="http://localhost:3000/sucesso?sessao_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:3000/cancelado",
            metadata={
                "id_pedido": str(pagamento.id_pedido),
                "id_usuario": str(id_usuario_seguro),
                "id_produto": str(pagamento.id_produto),
            }
        )
    except stripe.error.StripeError as erro:
        raise HTTPException(status_code=400, detail=f"Erro no Stripe: {str(erro)}")

    # Salvamos a transação no nosso banco local para auditoria
    nova_transacao = Transacao(
        id_pedido=pagamento.id_pedido,
        id_usuario=id_usuario_seguro, # Usando o ID validado pelo JWT
        valor=pagamento.valor,
        id_sessao_stripe=sessao.id,
        status="CRIADO"
    )
    banco.add(nova_transacao)
    banco.commit()
    banco.refresh(nova_transacao)

    # Retornamos a URL do Stripe para o frontend redirecionar
    resposta = TransacaoResposta(
        id=nova_transacao.id,
        id_pedido=nova_transacao.id_pedido,
        id_sessao_stripe=nova_transacao.id_sessao_stripe,
        status=nova_transacao.status,
        url_checkout=sessao.url
    )
    return resposta


# ========================
# ROTA 2: Confirmar Pagamento Manualmente (Síncrono)
# ========================
@roteador.get("/confirmar-pagamento/{id_sessao}")
def confirmar_pagamento_manual(id_sessao: str, banco: Session = Depends(obter_banco)):
    """
    Consulta o Stripe diretamente para verificar se a sessão foi paga.
    Isso substitui a necessidade do Webhook/Stripe CLI em ambiente de teste.
    """
    try:
        # Consultamos o Stripe
        sessao = stripe.checkout.Session.retrieve(id_sessao)
        
        if sessao.payment_status == "paid":
            # Se foi pago, atualizamos o banco e liberamos o ativo
            transacao = banco.query(Transacao).filter(
                Transacao.id_sessao_stripe == id_sessao
            ).first()

            if transacao:
                if transacao.status != "PAGO":
                    transacao.status = "PAGO"
                    banco.commit()

                # SEMPRE tentamos publicar o sucesso, para garantir que o Ativo seja liberado
                # mesmo que o primeiro sinal tenha falhado.
                metadados = sessao.get("metadata", {})
                publicar_pagamento_sucesso({
                    "id_pedido": int(metadados.get("id_pedido", 0)),
                    "id_usuario": int(metadados.get("id_usuario", 0)),
                    "id_produto": int(metadados.get("id_produto", 0)),
                    "id_sessao_stripe": id_sessao,
                    "valor": transacao.valor,
                })
                return {"sucesso": True, "status": "PAGO", "mensagem": "Sinal de liberação enviado!"}
        
        return {"sucesso": False, "status": sessao.payment_status, "mensagem": "Pagamento ainda nao confirmado."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar pagamento: {str(e)}")

# ========================
# ROTA 3: Webhook do Stripe (Opcional agora)
# ========================
@roteador.post("/webhook")
async def webhook_stripe(request: Request, banco: Session = Depends(obter_banco)):
    """
    Recebe eventos assíncronos do Stripe (Webhook).
    """
    corpo = await request.body()
    assinatura = request.headers.get("Stripe-Signature")

    print(f"\n[STRIPE] Webhook recebido! Assinatura detectada.")

    try:
        evento = stripe.Webhook.construct_event(
            corpo, assinatura, STRIPE_WEBHOOK_SECRETO
        )
    except ValueError:
        print("[ERRO] Payload invalido")
        raise HTTPException(status_code=400, detail="Payload do webhook invalido.")
    except stripe.error.SignatureVerificationError:
        print("[ERRO] Assinatura invalida! Verifique o STRIPE_WEBHOOK_SECRETO")
        raise HTTPException(status_code=400, detail="Assinatura do webhook invalida.")

    # Processamos apenas o evento de checkout concluído com sucesso
    if evento["type"] == "checkout.session.completed":
        sessao = evento["data"]["object"]
        id_sessao = sessao["id"]
        metadados = sessao.get("metadata", {})

        # Atualizamos o status da transação no nosso banco
        transacao = banco.query(Transacao).filter(
            Transacao.id_sessao_stripe == id_sessao
        ).first()

        if transacao:
            transacao.status = "PAGO"
            banco.commit()

            # Avisamos o Serviço de Ativos que o pagamento foi confirmado
            publicar_pagamento_sucesso({
                "id_pedido": int(metadados.get("id_pedido", 0)),
                "id_usuario": int(metadados.get("id_usuario", 0)),
                "id_produto": int(metadados.get("id_produto", 0)),
                "id_sessao_stripe": id_sessao,
                "valor": transacao.valor,
            })

    return {"recebido": True}
