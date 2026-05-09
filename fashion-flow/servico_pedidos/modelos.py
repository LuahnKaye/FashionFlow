from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from banco_de_dados import Base

class Pedido(Base):
    """
    Representa uma intenção de compra no sistema.
    """
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, nullable=False)
    id_produto = Column(Integer, nullable=False)
    quantidade = Column(Integer, default=1)
    preco_total = Column(Float, nullable=False)
    
    # Status iniciais: PENDENTE, AGUARDANDO_PAGAMENTO, CONCLUIDO, CANCELADO
    status = Column(String, default="PENDENTE")
    
    data_criacao = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Pedido(id={self.id}, status={self.status})>"
