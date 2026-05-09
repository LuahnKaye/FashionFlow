# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PedidoBase(BaseModel):
    id_produto: int
    quantidade: int
    preco_total: float

class PedidoCriar(PedidoBase):
    pass

class PedidoResposta(PedidoBase):
    id: int
    id_usuario: int
    status: str
    data_criacao: datetime

    class Config:
        from_attributes = True
