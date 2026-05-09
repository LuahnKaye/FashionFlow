from sqlalchemy import create_all, create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
import os

# Configurações do Banco
DB_URL = "postgresql://usuario_loja:senha_loja@localhost:5432/fashionflow"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()
transacoes = Table('transacoes', metadata, autoload_with=engine)

print("\n--- RELATÓRIO DE TRANSAÇÕES ---")
registros = session.query(transacoes).all()
if not registros:
    print("Nenhuma transação encontrada no banco!")
else:
    for r in registros:
        print(f"ID: {r.id} | Pedido: {r.id_pedido} | Status: {r.status} | Stripe: {r.id_sessao_stripe}")
print("-------------------------------\n")

session.close()
