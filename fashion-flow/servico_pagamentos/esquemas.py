from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PagamentoCriar(BaseModel):
    """Payload que o frontend envia para iniciar o checkout."""
    id_pedido: int
    id_usuario: int
    id_produto: int
    valor: float
    nome_produto: str = "Produto FashionFlow"

class TransacaoResposta(BaseModel):
    """Resposta retornada ao frontend após criar a sessão."""
    id: int
    id_pedido: int
    id_sessao_stripe: Optional[str]
    status: str
    url_checkout: Optional[str] = None

    class Config:
        from_attributes = True
