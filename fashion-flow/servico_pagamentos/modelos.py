from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from banco_de_dados import Base

class Transacao(Base):
    """
    Registra cada tentativa de pagamento e seu resultado.
    Funciona como um log financeiro imutável.
    """
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, nullable=False, index=True)
    id_usuario = Column(Integer, nullable=False)
    valor = Column(Float, nullable=False)

    # O ID da sessão de checkout gerado pelo Stripe
    id_sessao_stripe = Column(String, unique=True, nullable=True)

    # Status possíveis: CRIADO, PAGO, FALHOU, REEMBOLSADO
    status = Column(String, default="CRIADO")

    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Transacao(id={self.id}, pedido={self.id_pedido}, status={self.status})>"
