import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from banco_de_dados import motor_do_banco, Base
from rotas_pedidos import roteador
from consumidor import iniciar_consumidor

# Cria as tabelas no banco caso não existam
Base.metadata.create_all(bind=motor_do_banco)

app = FastAPI(
    title="FashionFlow - Serviço de Pedidos",
    description="Responsável pela orquestração de novas compras e comunicação via RabbitMQ."
)

# --- CONFIGURAÇÃO DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Simplificado para evitar erros de desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(roteador)

@app.on_event("startup")
def iniciar_servicos_segundo_plano():
    """
    Inicia o consumidor RabbitMQ em uma thread separada.
    """
    print("[INFO] Iniciando consumidor de Pedidos em segundo plano...")
    thread = threading.Thread(target=iniciar_consumidor, daemon=True)
    thread.start()

@app.get("/")
def verificar_saude():
    return {"status": "Serviço de Pedidos operando!"}
