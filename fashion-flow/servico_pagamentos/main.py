from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from banco_de_dados import motor_do_banco, Base
from rotas_pagamentos import roteador

# Cria as tabelas no banco 'bd_pagamentos' caso ainda nao existam
Base.metadata.create_all(bind=motor_do_banco)

app = FastAPI(
    title="FashionFlow - Servico de Pagamentos",
    description="Gerencia sessoes de checkout Stripe e webhooks de confirmacao."
)

# --- CONFIGURAÇÃO DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(roteador)

@app.get("/")
def verificar_saude():
    """Endpoint de saude do servico de pagamentos."""
    return {"status": "Servico de Pagamentos ativo e pronto para transacoes!"}
