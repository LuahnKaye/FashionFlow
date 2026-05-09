import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Se a variável DATABASE_URL estiver presente (Docker), usamos ela.
# Caso contrário, usamos o SQLite local para desenvolvimento simples.
URL_DO_BANCO = os.getenv("DATABASE_URL", "sqlite:///./identidade.db")

# O motor_do_banco é a "ponte" responsável por se comunicar de fato com o PostgreSQL
motor_do_banco = create_engine(URL_DO_BANCO, connect_args={"check_same_thread": False} if "sqlite" in URL_DO_BANCO else {})

# A SessaoLocal funciona como uma "aba" ou "conversa" isolada com o banco
SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor_do_banco)

# Base para que as nossas tabelas possam ser definidas no Python e mapeadas pro banco
Base = declarative_base()

def obter_banco():
    """
    Fornece uma sessão de banco de dados para cada requisição e garante o fechamento.

    Returns:
        SessaoLocal: Instância da sessão ativa conectada ao banco de dados.
    """
    banco = SessaoLocal()
    try:
        # yield suspende a execução e passa o 'banco' para quem chamou (o FastAPI). 
        # Depois que a requisição acaba, o código volta a rodar e cai no finally.
        yield banco
    finally:
        banco.close()
