# pyrefly: ignore [missing-import]
from fastapi import Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from fastapi.security import OAuth2PasswordBearer
# pyrefly: ignore [missing-import]
import jwt
# pyrefly: ignore [missing-import]
from pydantic import ValidationError
from seguranca import CHAVE_SECRETA, ALGORITMO

# O OAuth2PasswordBearer é uma funcionalidade nativa do FastAPI.
# Ele diz à API que nós esperamos um Token no cabeçalho Authorization com a palavra "Bearer ".
# O parâmetro tokenUrl="login" ajuda o painel de documentação (/docs) a saber onde fazer o login.
esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="login")

def verificar_token_acesso(token: str = Depends(esquema_oauth2)) -> dict:
    """
    Este é o nosso "Segurança de Porta" (Middleware). Ele abre o pacote (Token) e vê se é autêntico.
    Esse mesmo código será compartilhado com o Serviço de Pedidos e Estoque no futuro.

    Args:
        token (str): A string do JWT extraída automaticamente pelo FastAPI.

    Returns:
        dict: O conteúdo do token (o payload, contendo o id_usuario).

    Raises:
        HTTPException: Se o token for falso, tiver sido alterado ou estiver vencido.
    """
    erro_credenciais = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais. O token pode estar inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # A magia acontece aqui. O jwt.decode só funciona se o token tiver sido assinado
        # com a nossa CHAVE_SECRETA e ainda estiver no prazo de validade (exp).
        payload = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        
        # Recuperamos o id_usuario que salvamos na hora do login.
        id_usuario: int = payload.get("id_usuario")
        
        if id_usuario is None:
            raise erro_credenciais
            
        return payload
        
    except (jwt.PyJWTError, ValidationError):
        # Se qualquer coisa der errado na decodificação (ex: hacker alterou o token), rejeitamos.
        raise erro_credenciais
