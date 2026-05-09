# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from banco_de_dados import motor_do_banco, Base
from rotas_autenticacao import roteador

# Este comando pede pro SQLAlchemy criar todas as tabelas se elas não existirem
# Normalmente usaríamos uma ferramenta como Alembic para isso em produção
Base.metadata.create_all(bind=motor_do_banco)

app = FastAPI(
    title="FashionFlow - Serviço Identidade",
    description="Responsável por gerar os Tokens JWT e gerenciar os usuários."
)

# --- CONFIGURAÇÃO DE CORS ---
# Permite que o frontend (porta 3000) acesse esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos o roteador criado em rotas_autenticacao.py no app principal
app.include_router(roteador)

@app.get("/")
def verificar_saude():
    """
    Endpoint simples usado para verificar se o serviço está funcionando.

    Returns:
        dict: O status de funcionamento.
    """
    return {"status": "Serviço Identidade rodando perfeitamente!"}
