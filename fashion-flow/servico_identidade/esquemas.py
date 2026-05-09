# pyrefly: ignore [missing-import]
from pydantic import BaseModel, EmailStr

class UsuarioCriar(BaseModel):
    nome: str | None = None
    email: EmailStr
    senha: str

class UsuarioResposta(BaseModel):
    id: int
    nome: str | None = None
    email: EmailStr
    esta_ativo: bool

    class Config:
        # Permite que o Pydantic entenda o modelo retornado pelo SQLAlchemy
        from_attributes = True

class TokenAcesso(BaseModel):
    """
    Esquema que formata o retorno após um login bem sucedido.
    """
    token_acesso: str
    tipo_token: str
