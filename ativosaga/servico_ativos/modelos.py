from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from banco_de_dados import Base

class BibliotecaUsuario(Base):
    """
    Representa um ativo digital (imagem de produto) que o usuario comprou.
    Cada registro significa que o usuario tem acesso permanente ao produto.
    """
    __tablename__ = "biblioteca_usuario"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, nullable=False, index=True)
    id_pedido = Column(Integer, nullable=False)
    id_produto = Column(Integer, nullable=False)

    # URL da imagem em alta resolucao (liberada apos pagamento)
    url_imagem = Column(String, nullable=True)

    # Status: LIBERADO, REVOGADO
    status = Column(String, default="LIBERADO")

    data_liberacao = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Ativo(usuario={self.id_usuario}, produto={self.id_produto}, status={self.status})>"
