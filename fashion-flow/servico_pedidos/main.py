from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from banco_de_dados import motor_do_banco, Base
from rotas_pedidos import roteador

# Cria as tabelas no banco 'bd_pedidos' caso não existam
Base.metadata.create_all(bind=motor_do_banco)

app = FastAPI(
    title="FashionFlow - Serviço de Pedidos",
    description="Responsável pela orquestração de novas compras e comunicação via RabbitMQ."
)

# --- CONFIGURAÇÃO DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(roteador)

@app.get("/")
def verificar_saude():
    return {"status": "Serviço de Pedidos operando e pronto para receber ordens!"}
