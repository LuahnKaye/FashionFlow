import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Lê a URL do ambiente (Docker) ou usa o padrão local
URL_DO_BANCO = os.getenv("DATABASE_URL", "postgresql://postgres:senha_postgres@localhost:5432/bd_estoque")

motor_do_banco = create_engine(URL_DO_BANCO)
SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor_do_banco)
Base = declarative_base()

def obter_banco():
    banco = SessaoLocal()
    try:
        yield banco
    finally:
        banco.close()
