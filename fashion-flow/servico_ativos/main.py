import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from banco_de_dados import motor_do_banco, Base, obter_banco
from modelos import BibliotecaUsuario
from pydantic import BaseModel
from typing import List
from datetime import datetime
import threading
from consumidor import iniciar_consumidor

# Inicializa as tabelas
Base.metadata.create_all(bind=motor_do_banco)

app = FastAPI(
    title="FashionFlow - Servico de Ativos",
    description="Gerencia a biblioteca de ativos digitais comprados pelo usuario."
)

# --- CONFIGURAÇÃO DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Função para rodar o consumidor em segundo plano
def rodar_consumidor():
    print("[INFO] Iniciando consumidor RabbitMQ em segundo plano...")
    iniciar_consumidor()

@app.on_event("startup")
def iniciar_servicos_background():
    thread = threading.Thread(target=rodar_consumidor, daemon=True)
    thread.start()

# Configuracao JWT (mesma chave dos outros servicos)
CHAVE_SECRETA = "minha_chave_ultra_secreta_aqui_para_assinatura"
ALGORITMO = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verificar_token_acesso(token: str = Depends(oauth2_scheme)) -> dict:
    """Valida o Token JWT e extrai o payload."""
    try:
        payload = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        if payload.get("id_usuario") is None:
            raise HTTPException(status_code=401, detail="Token invalido.")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")

class AtivoResposta(BaseModel):
    id: int
    id_produto: int
    url_imagem: str
    status: str
    data_liberacao: datetime

    class Config:
        from_attributes = True

@app.get("/minha-biblioteca", response_model=List[AtivoResposta])
def listar_minha_biblioteca(
    dados_token: dict = Depends(verificar_token_acesso),
    banco: Session = Depends(obter_banco)
):
    """
    Retorna todos os ativos digitais que o usuario logado ja comprou.
    """
    id_usuario = dados_token.get("id_usuario")
    ativos = banco.query(BibliotecaUsuario).filter(
        BibliotecaUsuario.id_usuario == id_usuario,
        BibliotecaUsuario.status == "LIBERADO"
    ).all()
    return ativos

@app.get("/")
def verificar_saude():
    return {"status": "Servico de Ativos ativo e protegendo seus produtos!"}
