from sqlalchemy import Column, Integer
from banco_de_dados import Base

class Estoque(Base):
    """
    Controla a quantidade de itens físicos disponíveis para venda.
    """
    __tablename__ = "estoque"

    id = Column(Integer, primary_key=True, index=True)
    id_produto = Column(Integer, unique=True, nullable=False, index=True)
    quantidade_disponivel = Column(Integer, default=0)
    quantidade_reservada = Column(Integer, default=0)

    def __repr__(self):
        return f"<Estoque(produto={self.id_produto}, disponivel={self.quantidade_disponivel})>"
