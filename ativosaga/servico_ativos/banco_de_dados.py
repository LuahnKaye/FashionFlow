import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Banco isolado para a biblioteca de ativos digitais do usuario
URL_DO_BANCO = os.getenv("DATABASE_URL", "sqlite:///./ativos.db")

motor_do_banco = create_engine(
    URL_DO_BANCO, connect_args={"check_same_thread": False} if "sqlite" in URL_DO_BANCO else {}
)
SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor_do_banco)
Base = declarative_base()

def obter_banco():
    """
    Fornece uma sessao de banco de dados para cada requisicao.
    """
    banco = SessaoLocal()
    try:
        yield banco
    finally:
        banco.close()
